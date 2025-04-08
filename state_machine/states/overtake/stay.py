import time

from state_machine.components.base_state import BaseState
from state_machine.utils.detectors import check_dist_to_obj_sign, opposite_of_location


class StayState(BaseState):
    """Stay in the lane during overtaking."""

    NAME = "stay"

    def __init__(self, debug: bool = False):
        """Initialize the StayState."""
        from state_machine.states import overtake

        self.TRANSITIONS = {
            "loop": self.NAME,
            "overtake_done": overtake.SwitchLaneBackState.NAME,
        }
        super().__init__(debug)

    def execute(self, blackboard):
        """
        Execute the state.

        Arguments:
            blackboard -- The blackboard containing the state information

        Returns:
            str -- The next state to transition to
        """
        super().execute(blackboard)

        # Check if the overtaking is done
        if self.check_overtake_done():
            return "overtake_done"

        return "loop"

    def check_overtake_done(self):
        """Check if the overtaking is done."""
        from state_machine.states import CONSTANTS

        self._object_in_range = check_dist_to_obj_sign(
            self.object_list,
            ["vehicle"],
            CONSTANTS.OVERTAKE.START_DIST,
            location=opposite_of_location(self.car_location),
        )
        if not self._object_in_range:
            self._start_delay()
            if self._delay_start_time is not None:
                return (
                    time.perf_counter() - self._delay_start_time
                    > CONSTANTS.OVERTAKE.STAY_TIME
                )
        else:
            self._delay_start_time = None

        return False

    def _start_delay(self):
        """Delay before starting the state."""
        if self._delay_start_time is None:
            self._delay_start_time = time.perf_counter()
        else:
            self._delay_start_time = None
