import time

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard
from state_machine.states import CONSTANTS
from state_machine.states.overtake.switch_lane_back import SwitchLaneBackState
from state_machine.utils import Location
from state_machine.utils.detectors import check_dist_to_obj_sign


class StayState(BaseState):
    """Stay in the lane during overtaking."""

    NAME = "stay"

    def __init__(self, debug: bool = False):
        """Initialize the StayState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "overtake_done": SwitchLaneBackState.NAME,
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

        # Check if the overtaking is done
        if self.check_overtake_done():
            return "overtake_done"

        return "loop"

    def check_overtake_done(self):
        """Check if the overtaking is done."""
        self._object_in_range = check_dist_to_obj_sign(
            self.blackboard.objects,
            ["vehicle"],
            CONSTANTS.OVERTAKE.START_DIST,
            location=Location.opposite(self.blackboard.car_lane),
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
