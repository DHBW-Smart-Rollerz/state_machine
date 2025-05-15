class BARRED_AREA_CONSTANTS:
    """CONSTANTS for the bared area state machine."""

    # The distance to the object in front of the car when intersecting
    START_DIST = 400  # mm
    OBSTACLE_DIST = 1000  # mm
    APPROACH_DISTANCE = 400  # mm
    STAY_DISTANCE = 1500  # mm

    # The time in seconds until the ready state is canceled
    READY_TIMEOUT = 10
    NO_OBSTACLE_TIMEOUT = 3  # s
    WAIT_TIMEOUT = 10  # s
    TIMEOUT = 30  # s
    WAIT_DELAY = 3  # s

    # Maximum speed in m/s
    MAX_SPEED = 0.1  # m/s
    APPROACH_SPEED = 0.1  # m/s
    DETECT_SPEED = 0.1  # m/s (not allowed to stop)
