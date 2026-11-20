import time

from smarty_utils.enums import OBJECTS, Light

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.intersection.wait import WaitState
from state_machine.utils.detectors import check_dist_to_obj_sign


class GiveWayState(BaseState):
    """Handling give way intersection."""

    NAME = "intersection-give_way"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL, max_speed=0.0
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "done": "done",
            "wait_car": WaitState.NAME,
        }
        super().__init__(debug)

    def local_execute(self):
        """Execute the state."""
        super().local_execute()
        start_time = time.perf_counter()

        while (
            time.perf_counter() - start_time
            <= CONSTANTS.INTERSECTION.GIVE_NO_CAR_TIMEOUT
        ):
            if check_dist_to_obj_sign(
                self.blackboard.objects,
                [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
                CONSTANTS.INTERSECTION.VEHICLE_DIST,
            ):
                return "wait_car"

            time.sleep(0.0001)

            self.log_state("Intersection: Searching for vehicle")

        self.log_state("Intersection: No vehicle detected, continuing")
        return "done"
