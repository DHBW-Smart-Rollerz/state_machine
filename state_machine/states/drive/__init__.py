class DRIVE_CONSTANTS:
    """CONSTANTS for the drive state machine."""

    # Crosswalk Threshold
    CROSSWALK_THRESHOLD = 800  # mm

    # Barred Area Threshold
    BARRED_AREA_THRESHOLD = 800  # mm

    # Overtaking Threshold
    OVERTAKING_THRESHOLD = 900  # mm

    # Parking Area Threshold
    PARKING_THRESHOLD = 800  # mm

    # Intersection Threshold
    INTERSECTION_THRESHOLD = 600  # mm

    # Express Way Threshold
    EXPRESS_WAY_THRESHOLD = 800  # mm

    # No Passing Zone Threshold
    NO_PASSING_ZONE_THRESHOLD = 800  # mm

    # Maximum Speed
    MAX_SPEED = 1.0  # m/s

    OBSTACLE_DRIVE_SPEED = 0.5

    FREE_DRIVE_SPEED = 1.0

    # Distance of the lateral controller's reference point in front of the car.
    # The controller places the front axle at 0.26 m, so the look-ahead in front
    # of the axle is LOOKAHEAD_DISTANCE - 0.26. Larger = smoother, but cuts curves.
    LOOKAHEAD_DISTANCE = 0.0 # m

    # State Timeout
    STATE_TIMEOUT = 5  # seconds
