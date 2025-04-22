from smarty_utils.enums import SIGNS


class INTERSECTION_CONSTANTS:
    """CONSTANTS for the intersection state machine."""

    # The distance to the object in front of the car when overtaking
    START_DIST = 30  # mm
    START_OBJS = [SIGNS.STOP, SIGNS.GIVE_WAY]

    # The time in seconds until the overtaking is canceled
    TIMEOUT = 30  # s

    GIVE_WAY_MAX_SPEED = 0.3  # m/s
