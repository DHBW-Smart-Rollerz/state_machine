import time

from smarty_utils.enums import SIGNS, Light

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.intersection.give_way import GiveWayState
from state_machine.states.intersection.stop import StopState
from state_machine.utils.detectors import check_dist_to_obj_sign


class ReadyState(BaseState):
    """Ready for starting the overtaking."""

    NAME = "intersection-ready"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.INTERSECTION.MAX_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "start_stop": StopState.NAME,
            "start_give_way": GiveWayState.NAME,
            "canceled": "canceled",
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
        start = time.time()

        while time.time() - start < CONSTANTS.INTERSECTION.READY_TIMEOUT:
            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.STOP],
                CONSTANTS.INTERSECTION.START_DIST,
            ):
                return "start_stop"

            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.GIVE_WAY, SIGNS.PRIORITY_ONCOMING_TRAFFIC],
                CONSTANTS.INTERSECTION.START_DIST,
            ):
                return "start_give_way"

            self.log_state("Intersection: Searching for sign")

            time.sleep(0.0001)

        return "canceled"
