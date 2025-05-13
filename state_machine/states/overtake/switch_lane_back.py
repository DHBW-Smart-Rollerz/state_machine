from state_machine.components.generic_switch_lane import GenericSwitchLaneState


class SwitchLaneBackState(GenericSwitchLaneState):
    """Switch lane back after overtaking."""

    NAME = "overtake-switch_lane_back"

    def __init__(self, debug: bool = False):
        """Initialize the SwitchLaneBackState."""
        super().__init__("done", debug)
