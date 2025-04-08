from state_machine.states.drive.driving import DrivingState

__all__ = ["DrivingState"]


class DRIVE_CONSTANTS:
    """CONSTANTS for the drive state machine."""

    # Crosswalk Threshold
    CROSSWALK_THRESHOLD = 5.0  # meters

    # Barred Area Threshold
    BARRED_AREA_THRESHOLD = 5.0  # meters

    # Overtaking Threshold
    OVERTAKING_THRESHOLD = 5.0  # meters

    # Parking Area Threshold
    PARKING_AREA_THRESHOLD = 5.0  # meters

    # Intersection Threshold
    INTERSECTION_THRESHOLD = 5.0  # meters

    # Express Way Threshold
    EXPRESS_WAY_THRESHOLD = 5.0  # meters

    # No Passing Zone Threshold
    NO_PASSING_ZONE_THRESHOLD = 5.0  # meters
