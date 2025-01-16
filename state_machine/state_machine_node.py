from numpy import std
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

        self.get_logger().info("State Machine initialized")
        yasmin_viewer.YasminViewerPub("state_achine", self.sm)

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
                ("sign_topic", "/object_detection/sign"),
                ("object_topic", "/object_detection/object"),
            ],
        )

        # Get parameters from the ROS parameter server into a local variable
        self.debug = self.get_parameter("debug").value

    def init_publisher_and_subscriber(self):
        """Initializes the subscribers and publishers."""
        
        self.object_subscriber = self.create_subscription(
            msg_type=std_msgs.msg.Float32MultiArray,
            topic="/object_detection/objects",

        if self.debug:
            pass

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
