from smarty_utils.enums import SIGNS

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.utils.detectors import check_dist_to_obj_sign


class WaitState(BaseState):
    """Handling waiting on car to cross intersection."""

    NAME = "wait_intersection"
    STATE_DESCRIPTION = StateDescription(
        max_speed=0,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "done": "done",
        }
        super().__init__(debug)

    def execute(self, blackboard: BlackBoard):
        """
        Execute the state.

        Arguments:
            blackboard -- The blackboard containing the state information

        Returns:
            str -- The next state to transition to
        """
        super().execute(blackboard)

        # TODO: Implement the logic to check if the stop sign is detected

        return "loop"
