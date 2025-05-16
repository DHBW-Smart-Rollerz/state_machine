import copy
import time

import yasmin
from smarty_utils.enums import SIGNS, Light, Location, Nodes, NodeState

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.start_box.ready import ReadyState
from state_machine.utils import detectors


class SearchState(BaseState):
    """Search state class."""

    NAME = "startbox-search"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE_NORMAL,
        max_speed=0.0,
        goal_lane=Location.RIGHT_LANE,
        node_states={
            Nodes.OBJECT_DETECTION: NodeState.ACTIVE,
            Nodes.LANE_DETECTION: NodeState.INACTIVE,
            Nodes.PATH_PLANNING: NodeState.INACTIVE,
            Nodes.CONTROL: NodeState.INACTIVE,
            Nodes.STATE_ESTIMATION: NodeState.INACTIVE,
        },
    )

    def __init__(self, debug: bool = False):
        """Initializes the SearchState."""
        self.TRANSITIONS = {
            "canceled": "canceled",
            "start_sign_detected": ReadyState.NAME,
        }
        self._first_found_time = -1
        self._counter = 0
        super().__init__()

    def reset(self):
        """Reset the state."""
        self._first_found_time = -1
        self._counter = 0

    def local_execute(self, blackboard: BlackBoard) -> str:
        """
        Executes the SearchState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().local_execute(blackboard)

        while not self._is_start_box_detected(blackboard):
            self.log_state("Start Box: Waiting for stop sign to be detected")
            time.sleep(0.0001)
            if self._check_timeout():
                yasmin.YASMIN_LOG_WARN(
                    f"Start Box search timeout after {time.perf_counter() - self._init_time} seconds"
                )
                return "canceled"

        return "start_sign_detected"

    def _check_timeout(self) -> bool:
        """
        Check if the timeout for the search state has been reached.

        Returns:
            bool -- True if the timeout has been reached, False otherwise
        """
        timeout = CONSTANTS.START_BOX.SEARCH_TIMEOUT
        current_time = time.perf_counter()
        return current_time - self._init_time > timeout

    def _is_start_box_detected(self, blackboard: BlackBoard) -> bool:
        """
        Check if the start box is detected for more than 3 seconds, allowing brief interruptions.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            bool -- True if the start box is detected for the required duration, False otherwise
        """
        # return True
        # Stop sign in sign list
        signs: list[dict] = copy.copy(blackboard.signs)

        sign_dist_thresh = CONSTANTS.START_BOX.DISTANCE_THRESH
        ready_time_thresh = CONSTANTS.START_BOX.READY_TIME_THRESH
        forget_time_thresh = CONSTANTS.START_BOX.FORGET_READY_TIME_THRESH
        detected = detectors.check_dist_to_obj_sign(
            signs, SIGNS.STOP, sign_dist_thresh, Location.NOT_RELEVANT
        )

        current_time = time.perf_counter()

        if detected:
            if self._first_found_time < 0:
                self._first_found_time = current_time
            self._counter += 1
        else:
            if (
                self._first_found_time > 0
                and (current_time - self._first_found_time) > forget_time_thresh
            ):
                self.reset()

        if (
            self._first_found_time > 0
            and (current_time - self._first_found_time) > ready_time_thresh
        ):
            return True

        return False
