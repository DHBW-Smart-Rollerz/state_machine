from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard


class ParkingState(BaseState):
    """Parking state class."""

    NAME = "parking"

    def __init__(self, debug: bool = False):
        """Initializes the ParkingState."""
        # REQUIRED (Circular import)
        from state_machine.states.drive.driving import DrivingState

        self.TRANSITIONS = {"dummy": DrivingState.NAME}  # TODO: Add transitions
        super().__init__()

    def local_execute(self) -> str:
        """Executes the ParkingState."""
        super().local_execute()
        return "dummy"
