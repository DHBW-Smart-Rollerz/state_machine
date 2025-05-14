class CROSSWALK_CONSTANTS:
    """CONSTANTS for the intersection state machine."""

    # The distance to the object in front of the car when intersecting
    START_DIST = 400  # mm

    # The time in seconds until the ready state is canceled
    READY_TIMEOUT = 10

    # The time in seconds until the intersecting is canceled
    TIMEOUT = 30  # s

    # The distance to the object in front of the car when intersecting
    PEDESTRIAN_DIST = 1000  # mm

    # The minimal time to check for pedestrians
    NO_PEDESTRIAN_TIMEOUT = 3  # s

    # Maximum speed in m/s
    MAX_SPEED = 0.1  # m/s
