import math
import threading
import time

import geometry_msgs.msg
import numpy as np
import rclpy
import state_msgs.msg
import std_msgs.msg
import yasmin
from rclpy.parameter import Parameter
from rclpy.parameter_client import AsyncParameterClient
from smarty_utils.enums import (
    OBJECTS,
    SIGNS,
    Light,
    Location,
    Nodes,
    NodeState,
    StateMachineTestModes,
)
from smarty_utils.smarty_node import SmartyNode

from state_machine.components.state_description import BlackBoard
from state_machine.components.state_parameter import (
    ParameterStateParameter,
    StateParameter,
    TopicStateParameter,
)
from state_machine.states import CONSTANTS
from state_machine.states.barred_area.barred_area import BarredAreaState
from state_machine.states.cross_walk.crosswalk import CrosswalkStateMachine
from state_machine.states.drive.driving import DrivingState
from state_machine.states.intersection.express_way import ExpressWayState
from state_machine.states.intersection.intersection import IntersectionStateMachine
from state_machine.states.no_passing_zone.no_passing_zone import NoPassingZoneState
from state_machine.states.overtake.overtaking import OvertakingStateMachine
from state_machine.states.parking import ParkingState
from state_machine.states.start_box.startbox import StartBoxStateMachine
from state_machine.utils.detectors import check_dist_to_obj_sign, get_car_location
from state_machine.utils.object_detection_interface import create_obj_sign
from state_machine.webapp.app import create_and_run_flask_app


class StateMachine(SmartyNode):
    """State Machine."""

    def __init__(
        self, debug: bool = False, test_mode: int = StateMachineTestModes.NORMAL.value
    ):
        """Initialize the state machine."""
        super().__init__(
            "state_machine_node",
            "state_machine",
            node_parameters={
                # Subscriber topics
                "remote_state_subscriber": "/remoteState",
                "path_planning_left_subscriber": "/path_planning/target/left",
                "path_planning_right_subscriber": "/path_planning/target/right",
                "tracking_topic": "/tracking/state",
                "target_pose_topic": "/path_planning/target/pose",
                # Publisher topics
                "lights_topic": "/lights",
                "speed_limit_topic": "/control/velocity/target",
                "car_lane_topic": "/state_machine/car_lane",
                "goal_lane_topic": "/state_machine/goal_lane",
                "debug_state_topic": "/state_machine/debug/state",
                "drive_mode_topic": "/remote/drive_mode",
                # Parameters
                "debug": debug,
                "test_mode": test_mode,
            },
            subscribed_topics={
                "remote_state_subscriber": (
                    std_msgs.msg.UInt8,
                    self.new_remote_state,
                    None,
                ),
                "path_planning_left_subscriber": (
                    std_msgs.msg.Float32MultiArray,
                    self.new_left_lane,
                    None,
                ),
                "path_planning_right_subscriber": (
                    std_msgs.msg.Float32MultiArray,
                    self.new_right_lane,
                    None,
                ),
                "tracking_topic": (
                    state_msgs.msg.State,
                    self.tracking_callback,
                    None,
                ),
                "drive_mode_topic": (
                    std_msgs.msg.UInt8,
                    self.new_remote_state,
                    None,
                ),
            },
            published_topics={
                "lights_topic": (std_msgs.msg.UInt8, None),
                "speed_limit_topic": (std_msgs.msg.Float32, None),
                "debug_state_topic": (std_msgs.msg.String, None),
                "car_lane_topic": (std_msgs.msg.String, None),
                "goal_lane_topic": (std_msgs.msg.String, None),
                "target_pose_topic": (geometry_msgs.msg.Vector3, None),
                # TODO: For pathplannign -> Direction for driving (straight, left, right) NAME:  "path_planning_direction_topic": (std_msgs.msg.String, None)
            },
        )
        self._logger.set_level(rclpy.logging.LoggingSeverity.DEBUG)
        # Initialize the state machine
        self.node_state_clients = {
            node: AsyncParameterClient(self, node.value) for node in Nodes
        }
        self.blackboard = self.init_black_board()
        self.init_state_machine()

        # Execute the state machine
        self.speed_limit_thread = threading.Thread(
            target=self.speed_limit_fun, args=(self.blackboard,)
        )
        self.target_pose_thread = threading.Thread(
            target=self.target_pose_publisher_fun_thread, args=(self.blackboard,)
        )
        self.state_machine_thread = threading.Thread(
            target=self._run_sm, args=(self.blackboard,)
        )
        self.speed_limit_thread.daemon = True
        self.target_pose_thread.daemon = True
        self.state_machine_thread.daemon = True
        self.speed_limit_thread.start()
        self.target_pose_thread.start()
        self.state_machine_thread.start()

        if self._debug:
            self.get_logger().info("State machine initialized.")
            self.app_thread = threading.Thread(
                target=lambda: create_and_run_flask_app(self.blackboard),
            )
            self.app_thread.daemon = True
            self.app_thread.start()

    def init_black_board(self):
        """Create the black board object."""
        # Define the blackboard
        light_configuration = TopicStateParameter(
            "light_configuration", Light.BRAKE_NORMAL, Light, self.lights_publisher_fun
        )
        max_speed = TopicStateParameter(
            "max_speed", 0.0, float, self.speed_limit_publisher_fun, 30
        )
        goal_lane = TopicStateParameter(
            "goal_lane", Location.RIGHT, Location, self.goal_lane_publisher_fun
        )
        car_lane = TopicStateParameter(
            "car_lane", Location.RIGHT, Location, self.car_lane_publisher_fun
        )
        objects = StateParameter("objects", [], list[dict])
        signs = StateParameter("signs", [], list[dict])
        lane_coefficients = StateParameter("lane_coefficients", {}, dict[str, tuple])
        last_state = TopicStateParameter(
            "last_state", "initialized", str, self.debug_state_publisher_fun, 1
        )
        last_timestamp = StateParameter("last_timestamp", time.perf_counter(), float)
        node_states = {}
        for node in [
            Nodes.OBJECT_DETECTION,
            Nodes.LANE_DETECTION,
            Nodes.PATH_PLANNING,
            Nodes.CONTROL,
            Nodes.STATE_ESTIMATION,
            Nodes.TRACKING,
        ]:
            node_states[node] = ParameterStateParameter(
                f"{node.value}_state",
                NodeState.INACTIVE.value,
                int,
                [node],
                self.node_param_setter,
            )
        remote_state = StateParameter("remote_state", 0, int)

        return BlackBoard(
            light_configuration,
            max_speed,
            goal_lane,
            car_lane,
            objects,
            signs,
            lane_coefficients,
            last_state,
            last_timestamp,
            node_states,
            remote_state,
            int(self.get_parameter("test_mode").value),
        )

    def init_state_machine(self):
        """Create the state machine."""
        self.sm = yasmin.StateMachine(outcomes=["done", "canceled"])

        state_classes = [
            StartBoxStateMachine,
            DrivingState,
            IntersectionStateMachine,
            ParkingState,
            OvertakingStateMachine,
            CrosswalkStateMachine,
            ExpressWayState,
            NoPassingZoneState,
            BarredAreaState,
        ]
        [self._add_state(state_class) for state_class in state_classes]

    def _run_sm(self, custom_bb: BlackBoard):
        """Wrap the custom BlackBoard into a yasmin Blackboard and run the state machine."""
        self.sm(custom_bb)

    def _add_state(self, state_class: yasmin.State):
        """
        Add a state to the state machine.

        Arguments:
            state_class -- State Class
        """
        state: yasmin.State = state_class(self._debug)
        self.sm.add_state(name=state.NAME, state=state, transitions=state.TRANSITIONS)

    ##############################
    # Callbacks for the subscribers
    ##############################

    def tracking_callback(self, msg: state_msgs.msg.State):
        """Callback function for the object detection object subscriber."""
        objects = create_obj_sign(msg, self)
        self.blackboard.objects = [
            obj for obj in objects if isinstance(obj["name"], OBJECTS)
        ]
        self.blackboard.signs = [
            obj for obj in objects if isinstance(obj["name"], SIGNS)
        ]
        self.get_logger().info(
            f"Objects: {self.blackboard.objects}, Signs: {self.blackboard.signs}"
        )
        return True

    def new_remote_state(self, msg: std_msgs.msg.UInt8):
        """Callback function for the remote state subscriber."""
        # if self._debug:
        #     self.get_logger().info(f"Remote State: {msg.data}")
        self.blackboard.remote_state = msg.data
        return True

    def new_left_lane(self, msg: std_msgs.msg.Float32MultiArray):
        """Callback function for the left lane subscriber."""
        # Coefficients arrive in low-to-high order [a₀, a₁, a₂] → a₀ + a₁·x + a₂·x²
        line_coefs = list(msg.data)
        self.blackboard.lane_coefficients["left"] = np.poly1d(np.array(line_coefs))
        left_lane = self.blackboard.lane_coefficients.get("left", None)
        right_lane = self.blackboard.lane_coefficients.get("right", None)
        self.blackboard.car_lane = get_car_location(left_lane, right_lane)
        return True

    def new_right_lane(self, msg: std_msgs.msg.Float32MultiArray):
        """Callback function for the right lane subscriber."""
        # Coefficients arrive in low-to-high order [a₀, a₁, a₂] → a₀ + a₁·x + a₂·x²
        line_coefs = list(msg.data)
        self.blackboard.lane_coefficients["right"] = np.poly1d(np.array(line_coefs))
        left_lane = self.blackboard.lane_coefficients.get("left", None)
        right_lane = self.blackboard.lane_coefficients.get("right", None)
        self.blackboard.car_lane = get_car_location(left_lane, right_lane)
        return True

    ##############################
    # Callbacks for the publishers
    ##############################

    def lights_publisher_fun(self, light_configuration: Light):
        """Publish the light configuration."""
        msg = std_msgs.msg.UInt8()
        msg.data = light_configuration.value
        self.lights_topic.publish(msg)
        return True

    def speed_limit_publisher_fun(self, speed_limit: float):
        """Publish the speed limit."""
        msg = std_msgs.msg.Float32()
        msg.data = speed_limit
        self.speed_limit_topic.publish(msg)
        return True

    def car_lane_publisher_fun(self, car_lane: Location):
        """Publish the car lane."""
        msg = std_msgs.msg.String()
        msg.data = car_lane.value
        self.car_lane_topic.publish(msg)
        return True

    def goal_lane_publisher_fun(self, goal_lane: Location):
        """Publish the goal lane."""
        msg = std_msgs.msg.String()
        msg.data = goal_lane.value
        self.goal_lane_topic.publish(msg)
        return True

    def debug_state_publisher_fun(self, state: str):
        """Publish the debug state."""
        msg = std_msgs.msg.String()
        msg.data = f"{state}"
        self.debug_state_topic.publish(msg)
        return True

    def target_pose_publisher_fun(self, target_pose: dict):
        """Publish the target pose."""
        msg = geometry_msgs.msg.Vector3()
        msg.x = target_pose.get("x", 0.0)
        msg.y = target_pose.get("y", 0.0)
        msg.z = target_pose.get("z", 0.0)
        self.target_pose_topic.publish(msg)
        return True

    #################################
    # Target pose publisher thread
    #################################

    def _ref_point_controller(
        self, coefficients: dict[str, np.poly1d]
    ) -> tuple[float, float, float]:
        """
        Determines reference points for the controller based on the provided polynomial coefficients.

        Args:
            coefficients (list): List of coefficients representing the polynomial.

        Returns:
            tuple: Tuple containing (x, y, theta) representing the reference point coordinates and angle.
        """
        # coefficients is a np.poly1d (high-to-low order), already callable.
        # Evaluate the lane position and slope at a look-ahead of 0.1 m.
        x = 0.1  # look-ahead in metres
        y = coefficients(x)
        slope = coefficients.deriv()(x)  # dy/dx at x
        theta = math.atan(slope)
        return x, y, theta

    def target_pose_publisher_fun_thread(self, blackboard: BlackBoard):
        """
        Target pose publisher thread.

        Arguments:
            blackboard -- The blackboard containing the state information
        """
        while rclpy.ok():
            time.sleep(0.1)
            if blackboard.goal_lane in (Location.LEFT_LANE, Location.LEFT):
                target_coeffs = blackboard.lane_coefficients.get("left", None)
            elif blackboard.goal_lane in (Location.RIGHT_LANE, Location.RIGHT):
                target_coeffs = blackboard.lane_coefficients.get("right", None)
            else:
                target_coeffs = None

            if target_coeffs is None:
                continue

            ref_x, ref_y, theta = self._ref_point_controller(target_coeffs)

            if theta <= 0.3:
                theta = theta / 4

            self.target_pose_publisher_fun({"x": ref_x, "y": ref_y, "z": theta})

    #################################
    # Speed limit thread
    #################################

    def speed_limit_fun(self, blackboard: BlackBoard):
        """
        Speed limit thread.

        Arguments:
            blackboard -- The blackboard containing the state information
        """
        while rclpy.ok():
            time.sleep(0.001)
            if not blackboard._has_speed_limit and self._check_speed_limit(
                blackboard, lifted=False
            ):
                blackboard.speed_limit = CONSTANTS.SPEED_LIMIT_30
            elif blackboard._has_speed_limit and self._check_speed_limit(
                blackboard, lifted=True
            ):
                blackboard.reset_speed_limit()

    def _check_speed_limit(self, blackboard: BlackBoard, lifted: bool) -> bool:
        """
        Check if the speed limit is exceeded.

        Arguments:
            blackboard -- The blackboard containing the state information
            lifted -- True if the speed limit is lifted, False otherwise

        Returns:
            bool -- True if the speed limit is exceeded, False otherwise
        """
        if lifted:
            return check_dist_to_obj_sign(
                blackboard.signs,
                [SIGNS.SPEED_LIMIT_30_LIFTED],
                CONSTANTS.SPEED_LIMIT_THRESHOLD_30,
                location=Location.NOT_RELEVANT,
            )
        else:
            return check_dist_to_obj_sign(
                blackboard.signs,
                [SIGNS.SPEED_LIMIT_30],
                CONSTANTS.SPEED_LIMIT_THRESHOLD_30,
                location=Location.NOT_RELEVANT,
            )

    ################################
    # Parameter client
    ################################

    def node_param_setter(self, node: Nodes, params: list[Parameter]):
        """
        Set the parameter for the node.

        Arguments:
            node -- Node to publish the mode for
            params -- Parameters to set

        Returns:
            True if successful, False otherwise
        """
        if isinstance(params, Parameter):
            params = [params]
        for i in range(len(params)):
            if params[i].name.endswith("_state"):
                params[i]._name = "state"
        client = self.node_state_clients[node]

        self.get_logger().info(
            f"Setting parameter {params[0].name}:{params[0].value} for {node.value}"
        )
        future = client.set_parameters(params)
        future.add_done_callback(self.get_parameter_callback(node))
        return True

    def get_parameter_callback(self, node: Nodes):
        """
        Get the callback for the parameter setter.

        Arguments:
            node -- Node to get the callback for

        Returns:
            Callback function
        """
        temp = None

        # Callback function to handle the result of the parameter setting
        def callback(future):
            try:
                response = future.result()
                if self._debug:
                    self.get_logger().info(f"Set parameter {response} for {node.value}")
                return response
            except Exception as e:
                self.get_logger().error(
                    f"Failed to set parameter for {node.value}: {e}"
                )
            return False

        return callback

    def cancel_state(self):
        """Cancel the state machine."""
        self.sm.cancel_state()
        self.state_machine_thread.join()


def main(args=None, debug: bool = True):
    """
    Main function to start the StateMachine.

    Keyword Arguments:
        args -- Launch arguments (default: {None})
    """
    rclpy.init(args=args)
    node = StateMachine(debug=debug)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard interrupt, shutting down...")
    finally:
        node.cancel_state()
        node.destroy_node()

        # Shutdown if not already done by the ROS2 launch system
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main(debug=True)
