from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard


class ExpressWayState(BaseState):
    """Express way state class."""

    NAME = "express_way"

    def __init__(self, debug: bool = False):
        """Initializes the ExpressWayState."""
        # REQUIRED (Circular import)
        from state_machine.states.drive.driving import DrivingState

        self.TRANSITIONS = {"dummy": DrivingState.NAME}  # TODO: Add transitions
        super().__init__()

    def local_execute(self) -> str:
        """Executes the ExpressWayState."""
        super().local_execute()
        return "dummy"
