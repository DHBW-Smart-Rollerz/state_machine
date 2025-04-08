from state_machine.components.state_wrapped_sm import StateWrappedStateMachine
from state_machine.states import start_box


class StartBoxStateMachine(StateWrappedStateMachine):
    """Startbox state class."""

    NAME = "start_box"

    def __init__(self, debug: bool = False):
        """Initializes the StartBoxStateMachine."""
        from state_machine.states.drive.driving import DrivingState

        # External Transitions
        self.TRANSITIONS = {
            "done": DrivingState.NAME,
            "loop": self.NAME,
            "canceled": "canceled",
        }

        # Internal states
        state_classes = [
            start_box.SearchState,
            start_box.ReadyState,
        ]

        super().__init__(state_classes, debug)
