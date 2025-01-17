import yasmin

from state_machine.states.smarty import SmartyState


class BarredAreaState(SmartyState):
    """Barred area state."""

    NAME = "barred_area"

    def __init__(self):
        """Initializes the BarredAreaState."""
        # REQUIRED (Circular import)
        from state_machine.states.driving import DrivingState

        self.TRANSITIONS = {"dummy": DrivingState.NAME}  # TODO: Add transitions
        super().__init__()

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Executes the BarredAreaState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().execute(blackboard)
        return "dummy"
