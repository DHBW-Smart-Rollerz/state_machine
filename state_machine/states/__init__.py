from state_machine.states.barred_area import BARRED_AREA_CONSTANTS
from state_machine.states.cross_walk import CROSSWALK_CONSTANTS
from state_machine.states.drive import DRIVE_CONSTANTS
from state_machine.states.intersection import INTERSECTION_CONSTANTS
from state_machine.states.no_passing_zone import NO_PASSING_ZONE_CONSTANTS
from state_machine.states.overtake import OVERTAKE_CONSTANTS
from state_machine.states.start_box import START_BOX_CONSTANTS


class CONSTANTS:
    """CONSTANTS for the state machine."""

    START_BOX = START_BOX_CONSTANTS
    DRIVE = DRIVE_CONSTANTS
    OVERTAKE = OVERTAKE_CONSTANTS
    INTERSECTION = INTERSECTION_CONSTANTS
    CROSS_WALK = CROSSWALK_CONSTANTS
    BARRED_AREA = BARRED_AREA_CONSTANTS
    NO_PASSING_ZONE = NO_PASSING_ZONE_CONSTANTS

    # How fast the car can go when switching lanes
    MAX_SPEED_SWITCH_LANE = 0.2  # m/s
    LOG_TIME = 1  # s
    SPEED_LIMIT_30 = 0.83  # m/s
    SPEED_LIMIT_THRESHOLD_30 = 500  # mm
