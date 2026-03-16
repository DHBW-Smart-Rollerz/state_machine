import time

from smarty_utils.enums import SIGNS, Light

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.cross_walk.approach import ApproachCrosswalk
from state_machine.utils.detectors import check_dist_to_obj_sign


class ReadyState(BaseState):
    """Ready for starting the overtaking."""

    NAME = "cross-walk-ready"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.CROSS_WALK.MAX_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "approach": ApproachCrosswalk.NAME,
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
        start = time.perf_counter()

        while time.perf_counter() - start < CONSTANTS.CROSS_WALK.READY_TIMEOUT:
            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.CROSSWALK],
                CONSTANTS.CROSS_WALK.START_DIST,
            ):
                return "approach"

            self.log_state("Crosswalk: Searching for sign")

            time.sleep(0.0001)

        return "canceled"
