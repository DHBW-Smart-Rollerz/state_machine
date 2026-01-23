class CROSSWALK_CONSTANTS:
    """CONSTANTS for the intersection state machine."""

    # The distance to the object in front of the car when intersecting
    START_DIST = 600  # mm
    PEDESTRIAN_DIST = 1200  # mm
    APPROACH_DISTANCE = 500  # mm

    # The time in seconds until the ready state is canceled
    READY_TIMEOUT = 10
    NO_PEDESTRIAN_TIMEOUT = 3  # s
    TIMEOUT = 30  # s

    # Maximum speed in m/s
    MAX_SPEED = 0.1  # m/s
    APPROACH_SPEED = 0.1  # m/s
    DETECT_SPEED = 0.05  # m/s (not allowed to stop)
