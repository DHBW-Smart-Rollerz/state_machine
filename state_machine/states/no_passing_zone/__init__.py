class NO_PASSING_ZONE_CONSTANTS:
    """Constants for the no-passing zone state."""

    # Distance at which a leading vehicle triggers follow behaviour (mm)
    FOLLOW_DIST = 600  # mm

    # Safe following gap to maintain behind the leading vehicle (mm)
    SAFE_FOLLOWING_DIST = 400  # mm

    # Speed while following the leading vehicle (m/s)
    FOLLOW_SPEED = 0.15  # m/s

    # Normal cruise speed when no vehicle ahead (m/s)
    CRUISE_SPEED = 0.2  # m/s

    # Maximum time to stay in no-passing zone without a lifted sign (s)
    TIMEOUT = 60  # s

    # Distance threshold for the NO_OVERTAKING_LIFTED sign to end the state (mm)
    LIFTED_SIGN_DIST = 400  # mm
