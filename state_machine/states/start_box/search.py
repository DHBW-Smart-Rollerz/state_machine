import time

import yasmin

from state_machine.components.base_state import BaseState
from state_machine.states import start_box


class SearchState(BaseState):
    """Search state class."""

    NAME = "search_start_box"

    def __init__(self, debug: bool = False):
        """Initializes the SearchState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "canceled": "canceled",
            "start_sign_detected": start_box.ReadyState.NAME,
        }
        self._first_found_time = -1
        self._counter = 0
        super().__init__()

    def reset(self):
        """Reset the state."""
        self._first_found_time = -1
        self._counter = 0

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Executes the SearchState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- The outcome of the state
        """
        super().execute(blackboard)
        if self._is_start_box_detected(blackboard):
            return "start_sign_detected"
        elif self._check_timeout():
            yasmin.YASMIN_LOG_WARN(
                f"Start Box search timeout after {time.perf_counter() - self._init_time} seconds"
            )
            return "canceled"
        else:
            return "loop"

    def _check_timeout(self) -> bool:
        """
        Check if the timeout for the search state has been reached.

        Returns:
            bool -- True if the timeout has been reached, False otherwise
        """
        from state_machine.states import CONSTANTS

        timeout = CONSTANTS.START_BOX.SEARCH_TIMEOUT
        current_time = time.perf_counter()
        return current_time - self._init_time > timeout

    def _is_start_box_detected(self, blackboard: yasmin.Blackboard) -> bool:
        """
        Check if the start box is detected for more than 3 seconds, allowing brief interruptions.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            bool -- True if the start box is detected for the required duration, False otherwise
        """
        # Stop sign in sign list
        signs: list[dict] = blackboard["sign_list"]

        from state_machine.states import CONSTANTS

        sign_dist_thresh = CONSTANTS.START_BOX.DISTANCE_THRESH
        ready_time_thresh = CONSTANTS.START_BOX.READY_TIME_THRESH
        forget_time_thresh = CONSTANTS.START_BOX.FORGET_READY_TIME_THRESH
        detected = start_box.detect(signs, sign_dist_thresh)

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
