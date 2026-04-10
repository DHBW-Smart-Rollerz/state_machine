from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """
    Launch all uart nodes for controlling the car.

    Launch order:
      1. querregelung         — steering control
      2. uart_publisher       — publishes control commands to the car
      3. uart_subscriber      — subscribes to car status messages

    Returns:
        LaunchDescription
    """
    debug = LaunchConfiguration("debug")

    # ── Shared argument ───────────────────────────────────────────────────────
    declare_debug = DeclareLaunchArgument(
        "debug", default_value="False", description="Enable debug mode"
    )

    querregelung = Node(
        package="querregelung",
        executable="querregelung",
        name="querregelung",
        output="screen",
    )

    uart_publisher = Node(
        package="uart",
        executable="uart_publisher",
        name="uart_publisher",
        output="screen",
    )

    uart_subscriber = Node(
        package="uart",
        executable="uart_subscriber",
        name="uart_subscriber",
        output="screen",
    )

    # Build the list of entities, only include vimbax if available
    entities = []
    entities.append(declare_debug)
    entities.append(querregelung)
    entities.append(uart_publisher)
    entities.append(uart_subscriber)

    return LaunchDescription(entities)
