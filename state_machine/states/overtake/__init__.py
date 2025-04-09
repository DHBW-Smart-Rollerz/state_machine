class OVERTAKE_CONSTANTS:
    """CONSTANTS for the overtake state machine."""

    # The distance to the object in front of the car when overtaking
    START_DIST = 30  # mm

    # The time in seconds until the overtaking is canceled
    TIMEOUT = 30  # s

    # The time in seconds to stay in the lane after overtaking
    STAY_TIME = 5  # s

    # The maximum speed in m/s
    MAX_SPEED = 0.8  # m/s
