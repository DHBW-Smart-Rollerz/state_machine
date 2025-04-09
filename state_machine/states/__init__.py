from state_machine.states.drive import DRIVE_CONSTANTS
from state_machine.states.overtake import OVERTAKE_CONSTANTS
from state_machine.states.start_box import START_BOX_CONSTANTS


class CONSTANTS:
    """CONSTANTS for the state machine."""

    START_BOX = START_BOX_CONSTANTS
    DRIVE = DRIVE_CONSTANTS
    OVERTAKE = OVERTAKE_CONSTANTS

    # How fast the car can go when switching lanes
    MAX_SPEED_SWITCH_LANE = 0.8  # m/s
