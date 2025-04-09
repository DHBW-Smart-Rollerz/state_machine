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
                ): self.object_detection_mode_publisher_fun,
                NodesModes.get_publisher_name(
                    Nodes.LANE_DETECTION
                ): self.lane_detection_mode_publisher_fun,
                NodesModes.get_publisher_name(
                    Nodes.PATH_PLANNING
                ): self.path_planning_mode_publisher_fun,
                NodesModes.get_publisher_name(
                    Nodes.CONTROL
                ): self.control_mode_publisher_fun,
                NodesModes.get_publisher_name(
                    Nodes.STATE_ESTIMATION
                ): self.state_estimation_mode_publisher_fun,
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

    def object_callback(self, msg):
        """Callback function for the object detection object subscriber."""
        # Add the object to the blackboard
        objects = []
        for obj in msg.data:
            obj_id = 0  # TODO: Extract from Topic
            obj_position = 0  # TODO: Extract from Topic
            obj_dist = 0  # TODO: Extract from Topic
            obj_name = ID2OBJECT.get(obj_id, "unknown")
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
            sign_name = ID2SIGN.get(sign_id, "unknown")
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

    def speed_limit_publisher_fun(self, max_speed: float):
        """Publish the maximum speed."""
        msg = std_msgs.msg.Int16()
        msg.data = max_speed
        self.speed_limit_publisher.publish(msg)
        if self.debug:
            self.get_logger().info(f"Max Speed: {max_speed}")

    def lane_publisher_fun(self, goal_lane: Location):
        """Publish the goal lane."""
        # TODO
        if self.debug:
            self.get_logger().info(f"Goal Lane: {goal_lane}")

    def object_detection_mode_publisher_fun(self, mode: NodesModes):
        """Publish the object detection mode."""
        # TODO
        if self.debug:
            self.get_logger().info(f"Object Detection Mode: {mode}")

    def lane_detection_mode_publisher_fun(self, mode: NodesModes):
        """Publish the lane detection mode."""
        # TODO
        if self.debug:
            self.get_logger().info(f"Lane Detection Mode: {mode}")

    def path_planning_mode_publisher_fun(self, mode: NodesModes):
        """Publish the path planning mode."""
        # TODO
        if self.debug:
            self.get_logger().info(f"Path Planning Mode: {mode}")

    def control_mode_publisher_fun(self, mode: NodesModes):
        """Publish the control mode."""
        # TODO
        if self.debug:
            self.get_logger().info(f"Control Mode: {mode}")

    def state_estimation_mode_publisher_fun(self, mode: NodesModes):
        """Publish the state estimation mode."""
        # TODO
        if self.debug:
            self.get_logger().info(f"State Estimation Mode: {mode}")


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
