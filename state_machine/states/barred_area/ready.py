import time

from smarty_utils.enums import SIGNS, Light

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.barred_area.approach import ApproachBarredArea
from state_machine.states.barred_area.detect_obstacle import DetectObstacleState
from state_machine.states.drive import DRIVE_CONSTANTS
from state_machine.utils.detectors import check_dist_to_obj_sign


class ReadyState(BaseState):
    """Ready for starting the barred area."""

    NAME = "barred-area-ready"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.BARRED_AREA.MAX_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "barred_area": ApproachBarredArea.NAME,
            "barred_area_skip": DetectObstacleState.NAME,
            "canceled": "canceled",
        }
        super().__init__(debug)

    def local_execute(self):
        """Execute the state."""
        super().local_execute()
        start = time.perf_counter()

        while time.perf_counter() - start < CONSTANTS.BARRED_AREA.READY_TIMEOUT:
            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.PRIORITY_ONCOMING_TRAFFIC],
                CONSTANTS.BARRED_AREA.START_DIST,
            ):
                return "barred_area"
            # Skip if barred area sign not detected within drive threshold
            elif not check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.BARRED_AREA],
                DRIVE_CONSTANTS.BARRED_AREA_THRESHOLD,
            ):
                return "barred_area_skip"

            self.log_state("Barred Area: Searching for sign")

            time.sleep(0.0001)

        return "canceled"
