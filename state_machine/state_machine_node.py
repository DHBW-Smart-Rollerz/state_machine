import rclpy
import rclpy.node
import rclpy.wait_for_message
import yasmin
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
            ],
        )

        # Get parameters from the ROS parameter server into a local variable
        self.debug = self.get_parameter("debug").value

    def init_publisher_and_subscriber(self):
        """Initializes the subscribers and publishers."""

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
