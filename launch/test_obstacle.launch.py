import os

from ament_index_python import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """
    Launch the full obstacle-detection pipeline.

    Launch order:
      1. vimbax_camera        — camera driver
      2. camera_preprocessing — image preprocessing       ─┐ camera group
         (short delay)                                      │ wait 3 s before continuing
      3. lane_detection_ai    — lane line detection        ─┘
      4. object_detection     — object detector
      5. tracking             — object tracking
      6. pathplanning         — path planner

    Returns:
        LaunchDescription
    """
    debug = LaunchConfiguration("debug")

    # ── Shared argument ───────────────────────────────────────────────────────
    declare_debug = DeclareLaunchArgument(
        "debug", default_value="False", description="Enable debug mode"
    )
    # ── Camera group (launched immediately) ───────────────────────────────────
    vimbax = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                get_package_share_directory("vimbax_camera"),
                "/launch/vimbax_camera.launch.py",
            ]
        ),
        launch_arguments={"debug": debug}.items(),
    )

    camera_preprocessing = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                get_package_share_directory("camera_preprocessing"),
                "/launch/camera_preprocessing.launch.py",
            ]
        ),
        launch_arguments={"debug": debug}.items(),
    )

    # ── Downstream nodes (delayed 3 s to give the camera time to start) ───────
    CAMERA_STARTUP_DELAY = 3.0  # seconds

    lane_detection = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                get_package_share_directory("lane_detection_ai"),
                "/launch/lane_detection_ai.launch.py",
            ]
        ),
        launch_arguments={"debug": debug}.items(),
    )

    object_detection = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                get_package_share_directory("object_detection"),
                "/launch/object_detection.launch.py",
            ]
        ),
        launch_arguments={"debug": debug}.items(),
    )

    tracking = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                get_package_share_directory("tracking"),
                "/launch/object_tracking.launch.py",
            ]
        ),
        launch_arguments={"debug": debug}.items(),
    )

    pathplanning = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                get_package_share_directory("pathplanning"),
                "/launch/pathplanning.launch.py",
            ]
        ),
        launch_arguments={"debug": debug}.items(),
    )

    delayed_nodes = TimerAction(
        period=CAMERA_STARTUP_DELAY,
        actions=[
            lane_detection,
            object_detection,
            tracking,
            pathplanning,
        ],
    )

    return LaunchDescription(
        [
            declare_debug,
            # Camera group — start immediately
            vimbax,
            camera_preprocessing,
            # Everything else — start after camera is up
            delayed_nodes,
        ]
    )
