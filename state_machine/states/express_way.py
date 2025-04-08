import yasmin

from state_machine.components.base_state import BaseState


class ExpressWayState(BaseState):
    """Express way state class."""

    NAME = "express_way"

    def __init__(self, debug: bool = False):
        """Initializes the ExpressWayState."""
        # REQUIRED (Circular import)
        from state_machine.states.driving import DrivingState

        self.TRANSITIONS = {"dummy": DrivingState.NAME}  # TODO: Add transitions
        super().__init__()

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Executes the ExpressWayState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().execute(blackboard)
        return "dummy"
