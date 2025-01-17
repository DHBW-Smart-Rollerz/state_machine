import yasmin

from state_machine.states.smarty import SmartyState


class CrosswalkState(SmartyState):
    """Crosswalk state."""

    NAME = "crosswalk"

    def __init__(self):
        """Initializes the CrosswalkState."""
        # REQUIRED (Circular import)
        from state_machine.states.driving import DrivingState

        self.TRANSITIONS = {"dummy": DrivingState.NAME}  # TODO: Add transitions
        super().__init__()

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Executes the CrosswalkState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().execute(blackboard)
        return "dummy"
