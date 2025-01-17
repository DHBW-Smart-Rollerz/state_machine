import yasmin

from state_machine.states.smarty import SmartyState


class NoPassingZoneState(SmartyState):
    """NoPassingZone state class."""

    NAME = "no_passing_zone"

    def __init__(self):
        """Initializes the NoPassingZoneState."""
        # REQUIRED (Circular import)
        from state_machine.states.driving import DrivingState

        self.TRANSITIONS = {"dummy": DrivingState.NAME}  # TODO: Add transitions
        super().__init__()

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Executes the NoPassingZoneState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().execute(blackboard)
        return "dummy"
