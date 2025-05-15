from state_machine.components.generic_switch_lane import GenericSwitchLaneState


class SwitchLaneState(GenericSwitchLaneState):
    """Switch lane during overtaking."""

    NAME = "barred-area-switch-lane"

    def __init__(self, debug: bool = False):
        """Initialize the SwitchLaneState."""
        from state_machine.states.barred_area.stay import StayState

        super().__init__(StayState, debug)


class SwitchLaneBackState(GenericSwitchLaneState):
    """Switch lane back after overtaking."""

    NAME = "barred-area-switch-lane-back"

    def __init__(self, debug: bool = False):
        """Initialize the SwitchLaneBackState."""
        super().__init__("done", debug)
