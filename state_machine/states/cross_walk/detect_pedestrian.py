import time
import yasmin
from smarty_utils.enums import OBJECTS, Light

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.cross_walk.wait import WaitState
from state_machine.utils.detectors import check_dist_to_obj_sign


class DetectPedestrian(BaseState):
    """Handling crosswalk pedestrian."""

    NAME = "crosswalk-detect-pedestrian"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE_NORMAL,
        max_speed=CONSTANTS.CROSS_WALK.DETECT_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the DetectPedestrian."""
        self.TRANSITIONS = {
            "done": "done",
            "wait_pedestrian": WaitState.NAME,
        }
        super().__init__(debug)

    def local_execute(self):
        """Execute the state."""
        super().local_execute()
        start_time = self.blackboard.last_timestamp

        while (
            time.perf_counter() - start_time
            <= CONSTANTS.CROSS_WALK.NO_PEDESTRIAN_TIMEOUT
        ):
            if check_dist_to_obj_sign(
                self.blackboard.objects,
                [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
                CONSTANTS.CROSS_WALK.PEDESTRIAN_DIST,
            ):
                return "wait_pedestrian"

            time.sleep(0.0001)

            self.log_state("Cross Walk: Searching for pedestrian")

        self.log_state("Cross Walk: No pedestrian detected, continuing")
        return "done"
