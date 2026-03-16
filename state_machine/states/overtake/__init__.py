class OVERTAKE_CONSTANTS:
    """CONSTANTS for the overtake state machine."""

    # The distance to the object in front of the car when overtaking
    START_DIST = 500  # mm

    # The time in seconds until the overtaking is canceled
    TIMEOUT = 30  # s

    # The time in seconds to stay in the lane after overtaking
    # STAY_TIME = 5  # s
    STAY_DISTANCE = 200  # mm

    # The maximum speed in m/s
    MAX_SPEED = 0.2  # m/s
