import threading
import time

import geometry_msgs.msg
import numpy as np
import rclpy
from state_machine.utils.detectors import get_car_location
from state_machine.utils.object_detection_interface import create_obj_sign
import std_msgs.msg
import yasmin
import yasmin_viewer
from rclpy.parameter import Parameter
from rclpy.parameter_client import AsyncParameterClient
from smarty_utils.enums import Light, Location, Nodes, NodeState
from smarty_utils.smarty_node import SmartyNode

from state_machine.components.state_description import BlackBoard
from state_machine.components.state_parameter import (
    ParameterStateParameter,
    StateParameter,
    TopicStateParameter,
)
from state_machine.states.barred_area import BarredAreaState
from state_machine.states.crosswalk import CrosswalkState
from state_machine.states.drive.driving import DrivingState
from state_machine.states.intersection.express_way import ExpressWayState
from state_machine.states.intersection.intersection import IntersectionStateMachine
from state_machine.states.no_passing_zone import NoPassingZoneState
from state_machine.states.overtake.overtaking import OvertakingStateMachine
from state_machine.states.parking import ParkingState
from state_machine.states.start_box.startbox import StartBoxStateMachine
from state_machine.webapp.app import create_and_run_flask_app


class StateMachine(SmartyNode):
    """State Machine."""

    def __init__(self, debug: bool = False):
        """Initialize the state machine."""
        super().__init__(
            "state_machine_node",
            "state_machine",
            node_parameters={
                # Subscriber topics
                "remote_state_subscriber": "/remoteState",
                "path_planning_left_subscriber": "/path_planning/target/left",
                "path_planning_right_subscriber": "/path_planning/target/right",
                "sign_topic": "/object_detection/sign",
                "object_topic": "/object_detection/object",
                # Publisher topics
                "lights_topic": "/lights",
                "speed_limit_topic": "/control/velocity/target2",
                "car_lane_topic": "/state_machine/car_lane",
                "goal_lane_topic": "/state_machine/goal_lane",
                "debug_state_topic": "/state_machine/debug/state",
                # Parameters
                "debug": debug,
            },
            subscribed_topics={
                "remote_state_subscriber": (
                    std_msgs.msg.UInt8,
                    self.new_remote_state,
                    None,
                ),
                "path_planning_left_subscriber": (
                    geometry_msgs.msg.Vector3,
                    self.new_left_lane,
                    None,
                ),
                "path_planning_right_subscriber": (
                    geometry_msgs.msg.Vector3,
                    self.new_right_lane,
                    None,
                ),
                "sign_topic": (
                    std_msgs.msg.Float32MultiArray,
                    self.sign_callback,
                    None,
                ),
                "object_topic": (
                    std_msgs.msg.Float32MultiArray,
                    self.object_callback,
                    None,
                ),
            },
            published_topics={
                "lights_topic": (std_msgs.msg.UInt8, None),
                "speed_limit_topic": (std_msgs.msg.Float32, None),
                "debug_state_topic": (std_msgs.msg.String, None),
                "car_lane_topic": (std_msgs.msg.String, None),
                "goal_lane_topic": (std_msgs.msg.String, None),
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
        self.state_machine_thread = threading.Thread(
            target=lambda x: self.sm(x), args=(self.blackboard,)
        )
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
            "light_configuration", Light.BRAKE, Light, self.lights_publisher_fun
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
            CrosswalkState,
            ExpressWayState,
            NoPassingZoneState,
            BarredAreaState,
        ]
        [self._add_state(state_class) for state_class in state_classes]

        if self._debug:
            yasmin_viewer.YasminViewerPub("state_machine", self.sm)

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

    def object_callback(self, msg: std_msgs.msg.Float32MultiArray):
        """Callback function for the object detection object subscriber."""
        objects = create_obj_sign(msg, True, self)
        self.blackboard.objects = objects

    def sign_callback(self, msg: std_msgs.msg.Float32MultiArray):
        """Callback function for the object detection sign subscriber."""
        signs = create_obj_sign(msg, False, self)
        self.blackboard.signs = signs

    def new_remote_state(self, msg: std_msgs.msg.UInt8):
        """Callback function for the remote state subscriber."""
        if self._debug:
            self.get_logger().info(f"Remote State: {msg.data}")
        self.blackboard.remote_state = msg.data
        return True

    def new_left_lane(self, msg: geometry_msgs.msg.Vector3):
        """Callback function for the left lane subscriber."""
        line_coefs = [msg.x, msg.y, msg.z]
        self.blackboard.lane_coefficients["left"] = np.poly1d(line_coefs)
        left_lane = self.blackboard.lane_coefficients.get("left", None)
        right_lane = self.blackboard.lane_coefficients.get("right", None)
        self.blackboard.car_lane = get_car_location(left_lane, right_lane)
        return True

    def new_right_lane(self, msg: geometry_msgs.msg.Vector3):
        """Callback function for the right lane subscriber."""
        line_coefs = [msg.x, msg.y, msg.z]
        self.blackboard.lane_coefficients["right"] = np.poly1d(line_coefs)
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
                    self.get_logger().info(
                        f"Set parameter {response} for {node.value}"
                    )
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


def main(args=None, debug: bool = False):
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
