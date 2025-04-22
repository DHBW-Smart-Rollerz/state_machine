from smarty_utils.enums import SIGNS

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.intersection.wait import WaitState
from state_machine.utils import Location
from state_machine.utils.detectors import check_dist_to_obj_sign


class StopState(BaseState):
    """Handling stopping intersection."""

    NAME = "stop_intersection"
    STATE_DESCRIPTION = StateDescription(max_speed=0, goal_lane=Location.RIGHT)

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "done": "done",
            "wait_car": WaitState.NAME,
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
