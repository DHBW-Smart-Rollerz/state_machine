import time

from smarty_utils.enums import OBJECTS, Light

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.intersection.wait import WaitState
from state_machine.utils.detectors import check_dist_to_obj_sign


class GiveWayState(BaseState):
    """Handling give way intersection."""

    NAME = "give_way"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.INTERSECTION.GIVE_WAY_MAX_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "done": "done",
            "wait_car": WaitState.NAME,
        }
        self.start_time = time.perf_counter()
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

        while (
            time.perf_counter() - self.start_time
            <= CONSTANTS.INTERSECTION.NO_CAR_TIMEOUT
        ):
            if check_dist_to_obj_sign(
                self.blackboard.objects,
                [OBJECTS.VEHICLE],
                CONSTANTS.INTERSECTION.VEHICLE_DIST,
            ):
                return "wait_car"

            self.log_state("Intersection: Searching for vehicle")
            time.sleep(0.0001)

        return "done"
