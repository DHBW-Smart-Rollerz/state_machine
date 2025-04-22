class INTERSECTION_CONSTANTS:
    """CONSTANTS for the intersection state machine."""

    # The distance to the object in front of the car when overtaking
    START_DIST = 30  # mm

    # The time in seconds until the overtaking is canceled
    TIMEOUT = 30  # s

    # The maximum speed in m/s
    GIVE_WAY_MAX_SPEED = 0.5  # m/s

    # The distance to the object in front of the car when overtaking
    VEHICLE_DIST = 1000  # mm

    # The minimal time to check for cars
    NO_CAR_TIMEOUT = 3  # s

    # Maximum speed in m/s
    MAX_SPEED = 0.5  # m/s

    # The distance to the object in front of the car when overtaking
    LOG_TIME = 5  # s
