import rclpy
import rclpy.node
import rclpy.wait_for_message
import std_msgs.msg
import yasmin
import yasmin_viewer
from ament_index_python.packages import get_package_share_directory

from state_machine import states


class StateMachine(rclpy.node.Node):
    """State Machine."""

    def __init__(self):
        """Initialize the state machine."""
        super().__init__("state_machine")

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

        # Execute the state machine
        outcome = self.sm()
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

        self.sm = yasmin.StateMachine(outcomes=["done"])
        self.blackboard = yasmin.Blackboard()

        self.sm.add_state(
            name=states.StartboxState.NAME,
            state=states.StartboxState(),
            transitions=states.StartboxState.TRANSITIONS,
        )
        self.sm.add_state(
            name=states.DrivingState.NAME,
            state=states.DrivingState(),
            transitions=states.DrivingState.TRANSITIONS,
        )
        self.sm.add_state(
            name=states.IntersectionState.NAME,
            state=states.IntersectionState(),
            transitions=states.IntersectionState.TRANSITIONS,
        )
        self.sm.add_state(
            name=states.ParkingState.NAME,
            state=states.ParkingState(),
            transitions=states.ParkingState.TRANSITIONS,
        )
        self.sm.add_state(
            name=states.OvertakingState.NAME,
            state=states.OvertakingState(),
            transitions=states.OvertakingState.TRANSITIONS,
        )
        self.sm.add_state(
            name=states.CrosswalkState.NAME,
            state=states.CrosswalkState(),
            transitions=states.CrosswalkState.TRANSITIONS,
        )
        self.sm.add_state(
            name=states.ExpressWayState.NAME,
            state=states.ExpressWayState(),
            transitions=states.ExpressWayState.TRANSITIONS,
        )
        self.sm.add_state(
            name=states.NoPassingZoneState.NAME,
            state=states.NoPassingZoneState(),
            transitions=states.NoPassingZoneState.TRANSITIONS,
        )
        self.sm.add_state(
            name=states.BarredAreaState.NAME,
            state=states.BarredAreaState(),
            transitions=states.BarredAreaState.TRANSITIONS,
        )

        if self.debug:
            yasmin_viewer.YasminViewerPub("state_machine", self.sm)

    def object_callback(self, msg):
        """Callback function for the object detection object subscriber."""
        pass

    def sign_callback(self, msg):
        """Callback function for the object detection sign subscriber."""
        pass


def main(args=None):
    """
    Main function to start the StateMachine.

    Keyword Arguments:
        args -- Launch arguments (default: {None})
    """
    rclpy.init(args=args)
    node = StateMachine()

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
    main()
