from state_machine.states.overtake.overtaking import OvertakingStateMachine
from state_machine.states.overtake.ready import ReadyState
from state_machine.states.overtake.stay import StayState
from state_machine.states.overtake.switch_lane import SwitchLaneState
from state_machine.states.overtake.switch_lane_back import SwitchLaneBackState

__all__ = [
    "OvertakingStateMachine",
    "ReadyState",
    "SwitchLaneState",
    "StayState",
    "SwitchLaneBackState",
]


class OVERTAKE_CONSTANTS:
    """CONSTANTS for the overtake state machine."""

    # The distance to the object in front of the car when overtaking
    START_DIST = 30  # mm

    # The time in seconds until the overtaking is canceled
    TIMEOUT = 30  # s

    # The time in seconds to stay in the lane after overtaking
    STAY_TIME = 5  # s
