import time

from smarty_utils.enums import OBJECTS, Light, Location

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.barred_area.switch_lane import SwitchLaneState
from state_machine.states.barred_area.wait import WaitState
from state_machine.utils.detectors import check_dist_to_obj_sign


class DetectObstacleState(BaseState):
    """Handling Barred Area Cars."""

    NAME = "barred-area-detect-obstacle"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BLINK_LEFT_NORMAL,
        max_speed=CONSTANTS.BARRED_AREA.DETECT_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the DetectObstacleState."""
        self.TRANSITIONS = {
            "switch": SwitchLaneState.NAME,
            "wait": WaitState.NAME,
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
        start_time = blackboard.last_timestamp

        while (
            time.perf_counter() - start_time
            <= CONSTANTS.BARRED_AREA.NO_OBSTACLE_TIMEOUT
        ):
            if check_dist_to_obj_sign(
                self.blackboard.objects,
                [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
                CONSTANTS.BARRED_AREA.OBSTACLE_DIST,
                location=Location.LEFT_LANE,
            ):
                return "wait"

            time.sleep(0.0001)

            self.log_state("Barred Area: Searching for Vehicle or Pedestrian")

        self.log_state("Barred Area: Nothing detected, continuing")
        return "switch"
