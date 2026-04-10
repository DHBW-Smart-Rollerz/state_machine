from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction


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

    publish_control_active = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    "ros2",
                    "topic",
                    "pub",
                    "--once",
                    "/control/active",
                    "std_msgs/msg/Bool",
                    "{data: true}",
                ],
                output="screen",
            )
        ],
    )

    # Build the list of entities, only include vimbax if available
    entities = []
    entities.append(declare_debug)
    entities.append(querregelung)
    entities.append(uart_publisher)
    entities.append(uart_subscriber)
    entities.append(publish_control_active)

    return LaunchDescription(entities)
