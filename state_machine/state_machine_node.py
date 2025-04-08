import rclpy
import rclpy.node
import rclpy.wait_for_message
import std_msgs.msg
import yasmin
import yasmin_viewer
from ament_index_python.packages import get_package_share_directory

from state_machine import states
from state_machine.utils import Location

# from state_machine.states import STATE_NAME2STATE


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

        self.object_id_mapping = {  # TODO: load dynamically from yaml config file
            "vehicle": 2,
            "pedestrian": 10,
        }
        self.id_object_mapping = {v: k for k, v in self.object_id_mapping.items()}

        self.sign_id_mapping = {  # TODO: load dynamically from yaml config file
            "stop": 1,
            "no_overtaking": 3,
            "no_overtaking_lifted": 4,
            "fast_track": 5,
            "fast_track_lifted": 6,
            "speed_limit_30": 7,
            "speed_limit_30_lifted": 8,
            "crosswalk": 9,
            "priority_oncoming_traffic": 13,
            "parking": 14,
            "turn_left": 15,
            "turn_right": 16,
            "give_way": 17,
            "priority": 18,
        }
        self.id_sign_mapping = {v: k for k, v in self.sign_id_mapping.items()}

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
                ("speed_limit_topic", "/control/speed/limit"),
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

    def init_publisher_and_subscriber(self):
        """Initializes the subscribers and publishers."""
        self.sign_subscriber = self.create_subscription(
            std_msgs.msg.Float32MultiArray, self.sign_topic, self.sign_callback, 1
        )
        self.object_subscriber = self.create_subscription(
            std_msgs.msg.Float32MultiArray, self.object_topic, self.object_callback, 1
        )

        self.lights_publisher = self.create_publisher(
            std_msgs.msg.UInt8, self.lights_topic, 1
        )
        self.speed_limit_publisher = self.create_publisher(
            std_msgs.msg.Int16, self.speed_limit_topic, 1
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

        state_classes = [
            states.StartBoxStateMachine,
            states.DrivingState,
            states.IntersectionState,
            states.ParkingState,
            states.OvertakingState,
            states.CrosswalkState,
            states.ExpressWayState,
            states.NoPassingZoneState,
            states.BarredAreaState,
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

    def object_callback(self, msg):
        """Callback function for the object detection object subscriber."""
        # Add the object to the blackboard
        objects = []
        for obj in msg.data:
            obj_id = 0  # TODO: Extract from Topic
            obj_position = 0  # TODO: Extract from Topic
            obj_dist = 0  # TODO: Extract from Topic
            obj_name = self.id_object_mapping.get(obj_id, "unknown")
            objects.append(
                {
                    "id": obj_id,
                    "position": obj_position,
                    "distance": obj_dist,
                    "name": obj_name,
                    "timestamp": self.get_clock().now().nanoseconds,
                }
            )
        self.blackboard.set("object_list", objects)
        if self.debug:
            self.get_logger().info(f"Object List: {objects}")

    def sign_callback(self, msg):
        """Callback function for the object detection sign subscriber."""
        # Add the sign to the blackboard
        signs = []
        for sign in msg.data:
            sign_id = 0  # TODO: Extract from topic
            sign_position = 0  # TODO: Extract from topic
            sign_dist = 0  # TODO: Extract from topic
            sign_name = self.id_sign_mapping.get(sign_id, "unknown")
            signs.append(
                {
                    "id": sign_id,
                    "position": sign_position,
                    "distance": sign_dist,
                    "name": sign_name,
                    "timestamp": self.get_clock().now().nanoseconds,
                }
            )
        self.blackboard.set("sign_list", signs)
        if self.debug:
            self.get_logger().info(f"Sign List: {signs}")


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
