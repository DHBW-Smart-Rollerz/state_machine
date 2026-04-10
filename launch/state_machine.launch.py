import os

from ament_index_python import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """
    Generate the launch description.

    Returns:
        LaunchDescription -- The launch description.
    """
    python_executable = os.getenv("PYTHON_EXECUTABLE", "/usr/bin/python3")
    debug = LaunchConfiguration("debug")
    test_mode = LaunchConfiguration("test_mode")
    params_file = LaunchConfiguration("params_file")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "debug", default_value="False", description="Enable debug mode"
            ),
            DeclareLaunchArgument(
                 "test_mode", default_value="0b00", description="Enable test mode"
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=os.path.join(
                    get_package_share_directory("state_machine"),
                    "config",
                    "ros_params.yaml",
                ),
                description="Path to the ROS parameters file",
            ),
            Node(
                package="state_machine",
                namespace="",  # Is also the namespace for loading the params
                executable="state_machine_node",
                name="state_machine",
                parameters=[
                    {
                        "debug": debug,
                        "test_mode": test_mode
                    },
                    params_file,
                ],
                prefix=[python_executable],
            ),
        ]
    )
