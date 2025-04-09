import numpy as np
import rclpy
import rclpy.node
import rclpy.wait_for_message
import std_msgs.msg
import yasmin
import yasmin_viewer
from ament_index_python.packages import get_package_share_directory

from state_machine.components.state_description import (
    OBJECTS,
    SIGNS,
    Light,
    Nodes,
    NodesModes,
    StateDescription,
)
from state_machine.states.barred_area import BarredAreaState
from state_machine.states.crosswalk import CrosswalkState
from state_machine.states.drive.driving import DrivingState
from state_machine.states.express_way import ExpressWayState
from state_machine.states.intersection import IntersectionState
from state_machine.states.no_passing_zone import NoPassingZoneState
from state_machine.states.overtake.overtaking import OvertakingStateMachine
from state_machine.states.parking import ParkingState
from state_machine.states.start_box.startbox import StartBoxStateMachine
from state_machine.utils import Location

# from state_machine.states import STATE_NAME2STATE

global OBJECT2ID, ID2OBJECT, SIGN2ID, ID2SIGN
OBJECT2ID = {  # TODO: load dynamically from yaml config file
    OBJECTS.VEHICLE: 2,
    OBJECTS.PEDESTRIAN: 10,
}
ID2OBJECT = {v: k for k, v in OBJECT2ID.items()}
SIGN2ID = {  # TODO: load dynamically from yaml config file
    SIGNS.STOP: 1,
    SIGNS.NO_OVERTAKING: 3,
    SIGNS.NO_OVERTAKING_LIFTED: 4,
    SIGNS.FAST_TRACK: 5,
    SIGNS.FAST_TRACK_LIFTED: 6,
    SIGNS.SPEED_LIMIT_30: 7,
    SIGNS.SPEED_LIMIT_30_LIFTED: 8,
    SIGNS.CROSSWALK: 9,
    SIGNS.PRIORITY_ONCOMING_TRAFFIC: 13,
    SIGNS.PARKING: 14,
    SIGNS.TURN_LEFT: 15,
    SIGNS.TURN_RIGHT: 16,
    SIGNS.GIVE_WAY: 17,
    SIGNS.PRIORITY: 18,
}
ID2SIGN = {v: k for k, v in SIGN2ID.items()}


class StateMachine(rclpy.node.Node):
    """State Machine."""

    def __init__(self, debug: bool = False):
        """Initialize the state machine."""
        super().__init__("state_machine")
        self.debug = debug

        # Get the package path
        self.package_share_path = get_package_share_directory("state_machine")
        self.get_logger().info(f"Package Path: {self.package_share_path}")

        # Load the parameters from the ROS parameter server and initialize
        # the publishers and subscribers
        self.load_ros_params()
        self.init_publisher_and_subscriber()

        self.init_state_machine()

        # Execute the state machine
        outcome = self.sm(self.blackboard)
        self.get_logger().info(f"State Machine finished with outcome: {outcome}")

    def load_ros_params(self):
        """Gets the parameters from the ROS parameter server."""
        # All command line arguments from the launch file and parameters from the
        # yaml config file must be declared here with a default value.
        self.declare_parameters(
            namespace="",
            parameters=[
                ("debug", False),
                ("debug_state_topic", "/state_machine/debug/state"),
                ("sign_topic", "/object_detection/sign"),
                ("object_topic", "/object_detection/object"),
                ("lights_topic", "/lights"),
                ("lane_detection_topic", "/lane_detection/lane"),
                ("goal_lane_topic", "/state_machine/lane/goal"),
                # ("speed_limit_topic", "/control/velocity/limit"),
                ("speed_limit_topic", "/control/velocity/target"),
            ],
        )

        # Get parameters from the ROS parameter server into a local variable
        if not self.debug:
            self.debug = self.get_parameter("debug").value
        self.debug_state_topic = self.get_parameter("debug_state_topic").value
        self.sign_topic = self.get_parameter("sign_topic").value
        self.object_topic = self.get_parameter("object_topic").value
        self.lights_topic = self.get_parameter("lights_topic").value
        self.speed_limit_topic = self.get_parameter("speed_limit_topic").value
        self.goal_lane_topic = self.get_parameter("goal_lane_topic").value

    def init_publisher_and_subscriber(self):
        """Initializes the subscribers and publishers."""
        ### Create the subscribers ###

        self.sign_subscriber = self.create_subscription(
            std_msgs.msg.Float32MultiArray, self.sign_topic, self.sign_callback, 1
        )
        self.object_subscriber = self.create_subscription(
            std_msgs.msg.Float32MultiArray, self.object_topic, self.object_callback, 1
        )

        ### Create the publishers ###

        self.lights_publisher = self.create_publisher(
            std_msgs.msg.UInt8, self.lights_topic, 1
        )
        self.speed_limit_publisher = self.create_publisher(
            std_msgs.msg.Float32, self.speed_limit_topic, 1
        )

        self.goal_lane_publisher = self.create_publisher(
            std_msgs.msg.UInt8, self.goal_lane_topic, 1
        )

        self.node_publisher = {}
        for node in Nodes:
            name = f"/state_machine/{node.value}/status"
            self.node_publisher[node] = self.create_publisher(
                std_msgs.msg.UInt8, name, 1
            )

        if self.debug:
            self.debug_state_publisher = self.create_publisher(
                std_msgs.msg.String, self.debug_state_topic, 1
            )

    def init_state_machine(self):
        """Create the state machine."""
        self.sm = yasmin.StateMachine(outcomes=["done", "canceled"])

        # Define the blackboard
        self.blackboard = yasmin.Blackboard()
        self.blackboard["debug"] = self.debug
        self.blackboard["car_location"] = Location.RIGHT
        self.blackboard["last_state"] = None
        self.blackboard["last_state_time_stamp"] = None
        self.blackboard["object_list"] = []
        self.blackboard["sign_list"] = []
        self.blackboard["state_description"] = StateDescription(
            light_configuration=Light.BRAKE,
            max_speed=0.0,
            goal_lane=Location.RIGHT,
            node_modes={
                Nodes.OBJECT_DETECTION: NodesModes.INACTIVE,
                Nodes.LANE_DETECTION: NodesModes.INACTIVE,
                Nodes.PATH_PLANNING: NodesModes.INACTIVE,
                Nodes.CONTROL: NodesModes.INACTIVE,
                Nodes.STATE_ESTIMATION: NodesModes.INACTIVE,
            },
            publishers={
                "light_configuration": self.lights_publisher_fun,
                "max_speed": self.speed_limit_publisher_fun,
                "goal_lane": self.lane_publisher_fun,
                NodesModes.get_publisher_name(
                    Nodes.OBJECT_DETECTION
                ): self.get_publisher(Nodes.OBJECT_DETECTION),
                NodesModes.get_publisher_name(Nodes.LANE_DETECTION): self.get_publisher(
                    Nodes.LANE_DETECTION
                ),
                NodesModes.get_publisher_name(Nodes.PATH_PLANNING): self.get_publisher(
                    Nodes.PATH_PLANNING
                ),
                NodesModes.get_publisher_name(Nodes.CONTROL): self.get_publisher(
                    Nodes.CONTROL
                ),
                NodesModes.get_publisher_name(
                    Nodes.STATE_ESTIMATION
                ): self.get_publisher(Nodes.STATE_ESTIMATION),
            },
        )
        state_classes = [
            StartBoxStateMachine,
            DrivingState,
            IntersectionState,
            ParkingState,
            OvertakingStateMachine,
            CrosswalkState,
            ExpressWayState,
            NoPassingZoneState,
            BarredAreaState,
        ]
        [self._add_state(state_class) for state_class in state_classes]

        if self.debug:
            yasmin_viewer.YasminViewerPub("state_machine", self.sm)

    def _add_state(self, state_class: yasmin.State):
        """
        Add a state to the state machine.

        Arguments:
            state_class -- State Class
        """
        state: yasmin.State = state_class(self.debug)
        self.sm.add_state(name=state.NAME, state=state, transitions=state.TRANSITIONS)

    ##############################
    # Callbacks for the subscribers
    ##############################

    def parse_float32_multiarray(self, msg: std_msgs.msg.Float32MultiArray):
        """Parse the Float32MultiArray message."""
        assert isinstance(msg, std_msgs.msg.Float32MultiArray), "Invalid message type"
        return [msg.data[i] for i in range(len(msg.data))]

    def _calc_dist(self, obj_position: dict) -> float:
        """Calculate the distance from the car to the object."""
        assert isinstance(obj_position, dict), "Invalid object position type"
        x = obj_position["bottom_left_x"]
        y = obj_position["bottom_left_y"]
        left = np.linalg.norm([x, y])
        x = obj_position["bottom_right_x"]
        y = obj_position["bottom_right_y"]
        right = np.linalg.norm([x, y])
        return min(left, right)

    def _create_obj_sign(self, parsed: list) -> list[dict]:
        """
        Create a list of objects or signs from the parsed data.

        Arguments:
            parsed -- parsed data from the Float32MultiArray message

        Returns:
            list of objects or signs
        """
        results = []
        for obj in parsed:
            len(obj) >= 6, "Invalid object data"
            obj_id = obj[0]
            obj_position = {
                "bottom_left_x": obj[1],
                "bottom_left_y": obj[2],
                "bottom_right_x": obj[3],
                "bottom_right_y": obj[4],
            }
            obj_location = Location.UNKNOWN  # TODO: Find locations
            obj_dist = self._calc_dist(obj_position)
            obj_name = ID2OBJECT.get(obj_id, "unknown")
            results.append(
                {
                    "id": obj_id,
                    "position": obj_position,
                    "distance": obj_dist,
                    "location": obj_location,
                    "name": obj_name,
                    "timestamp": self.get_clock().now().nanoseconds,
                }
            )

    def object_callback(self, msg: std_msgs.msg.Float32MultiArray):
        """Callback function for the object detection object subscriber."""
        # Add the object to the blackboard
        parsed = self.parse_float32_multiarray(msg)
        objects = self._create_obj_sign(parsed)
        self.blackboard.set("object_list", objects)
        if self.debug:
            self.get_logger().info(f"Object List: {objects}")

    def sign_callback(self, msg: std_msgs.msg.Float32MultiArray):
        """Callback function for the object detection sign subscriber."""
        parsed = self.parse_float32_multiarray(msg)
        signs = self._create_obj_sign(parsed)
        self.blackboard.set("sign_list", signs)
        if self.debug:
            self.get_logger().info(f"Sign List: {signs}")

    ##############################
    # Callbacks for the publishers
    ##############################

    def lights_publisher_fun(self, light_configuration: Light):
        """Publish the light configuration."""
        msg = std_msgs.msg.UInt8()
        msg.data = light_configuration.value
        self.lights_publisher.publish(msg)
        if self.debug:
            self.get_logger().info(f"Light Configuration: {light_configuration}")
        return True

    def speed_limit_publisher_fun(self, max_speed: float):
        """Publish the maximum speed."""
        msg = std_msgs.msg.Float32()
        msg.data = max_speed
        self.speed_limit_publisher.publish(msg)
        if self.debug:
            self.get_logger().info(f"Max Speed: {max_speed}")
        return True

    def lane_publisher_fun(self, goal_lane: Location):
        """Publish the goal lane."""
        msg = std_msgs.msg.UInt8()
        mapping = {
            Location.LEFT: 1,
            Location.RIGHT: 0,
        }
        msg.data = mapping.get(goal_lane, 0)
        self.goal_lane_publisher.publish(msg)
        if self.debug:
            self.get_logger().info(f"Goal Lane: {goal_lane}")
        return True

    def get_publisher(self, node: Nodes) -> callable:
        """
        Get the publisher function for the node.

        Arguments:
            node -- Node to get the publisher for

        Returns:
            Publisher function
        """
        return lambda mode: self.node_publisher_fun(node, mode)

    def node_publisher_fun(self, node: Nodes, mode: NodesModes):
        """
        Publish the node mode.

        Arguments:
            node -- Node to publish the mode for
            mode -- Mode to publish

        Returns:
            True if successful, False otherwise
        """
        publisher = self.node_publisher[node]
        msg = std_msgs.msg.UInt8()
        msg.data = mode.value
        publisher.publish(msg)
        if self.debug:
            self.get_logger().info(f"{node.value} Mode: {mode}")
        return True


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
        if node.sm.is_running():
            node.sm.cancel_state()
    finally:
        node.destroy_node()

        # Shutdown if not already done by the ROS2 launch system
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main(debug=True)
