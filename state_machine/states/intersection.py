import yasmin

from state_machine.components.base_state import BaseState


class IntersectionState(BaseState):
    """Intersection state."""

    NAME = "intersection"

    def __init__(self, debug: bool = False):
        """Initializes the IntersectionState."""
        # REQUIRED (Circular import)
        from state_machine.states.drive.driving import DrivingState

        self.TRANSITIONS = {"dummy": DrivingState.NAME}  # TODO: Add transitions
        super().__init__()

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Executes the IntersectionState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().execute(blackboard)
        return "dummy"
