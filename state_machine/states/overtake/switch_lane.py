from state_machine.components.generic_switch_lane import GenericSwitchLaneState
from state_machine.states.overtake.stay import StayState


class SwitchLaneState(GenericSwitchLaneState):
    """Switch lane during overtaking."""

    NAME = "overtake-switch_lane"

    def __init__(self, debug: bool = False):
        """Initialize the SwitchLaneState."""
        super().__init__(StayState, debug)
