import yasmin

from state_machine.states.smarty import SmartyState


class StartboxState(SmartyState):
    """Startbox state class."""

    NAME = "startbox"

    def __init__(self):
        """Initializes the StartboxState."""
        # REQUIRED (Circular import)
        from state_machine.states import DrivingState

        self.TRANSITIONS = {
            "startbox_closed": self.NAME,
            "startbox_open": DrivingState.NAME,
        }
        super().__init__()

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Executes the StartboxState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().execute(blackboard)

        if self._is_startbox_open(blackboard):
            return "startbox_open"
        else:
            return "startbox_closed"

    def _is_startbox_open(self, blackboard: yasmin.Blackboard) -> bool:
        # stop sign not detected
        # or stop sign distance > 50cm
        return True
