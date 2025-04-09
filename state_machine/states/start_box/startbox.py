from state_machine.components.state_wrapped_sm import StateWrappedStateMachine
from state_machine.states.start_box.ready import ReadyState
from state_machine.states.start_box.search import SearchState


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
            SearchState,
            ReadyState,
        ]

        super().__init__(state_classes, debug)
