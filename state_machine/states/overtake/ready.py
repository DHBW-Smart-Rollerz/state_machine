from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.overtake.switch_lane import SwitchLaneState
from state_machine.utils.detectors import check_dist_to_obj_sign


class ReadyState(BaseState):
    """Ready for starting the overtaking."""

    NAME = "ready"
    STATE_DESCRIPTION = StateDescription(
        max_speed=CONSTANTS.OVERTAKE.MAX_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "start_overtake": SwitchLaneState.NAME,
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

        if check_dist_to_obj_sign(
            self.blackboard.objects,
            ["vehicle"],
            CONSTANTS.OVERTAKE.START_DIST,
            location=self.blackboard.car_lane,
        ):
            return "start_overtake"

        return "loop"
