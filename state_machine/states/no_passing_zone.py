from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard


class NoPassingZoneState(BaseState):
    """NoPassingZone state class."""

    NAME = "no_passing_zone"

    def __init__(self, debug: bool = False):
        """Initializes the NoPassingZoneState."""
        # REQUIRED (Circular import)
        from state_machine.states.drive.driving import DrivingState

        self.TRANSITIONS = {"dummy": DrivingState.NAME}  # TODO: Add transitions
        super().__init__()

    def local_execute(self, blackboard: BlackBoard) -> str:
        """
        Executes the NoPassingZoneState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().local_execute(blackboard)
        return "dummy"
