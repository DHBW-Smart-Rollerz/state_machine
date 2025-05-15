import time

from smarty_utils.enums import OBJECTS, Location

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.overtake.switch_lane_back import SwitchLaneBackState
from state_machine.utils.detectors import check_dist_to_obj_sign


class StayState(BaseState):
    """Stay in the lane during overtaking."""

    NAME = "overtake-stay"
    STATE_DESCRIPTION = StateDescription(
        max_speed=CONSTANTS.OVERTAKE.MAX_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the StayState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "overtake_done": SwitchLaneBackState.NAME,
        }
        super().__init__(debug)
        self._delay_start_time = None

    def local_execute(self, blackboard: BlackBoard):
        """
        Execute the state.

        Arguments:
            blackboard -- The blackboard containing the state information

        Returns:
            str -- The next state to transition to
        """
        super().local_execute(blackboard)

        # Check if the overtaking is done
        while not self.check_overtake_done():
            self.log_state("Overtake: Waiting for overtaking to be done")

            time.sleep(0.0001)

        return "overtake_done"

    def clac_stay_time(self):
        """Calculate the time to stay in the lane after overtaking."""
        return (CONSTANTS.OVERTAKE.STAY_DISTANCE / 1000) / self.blackboard.max_speed

    def check_overtake_done(self):
        """Check if the overtaking is done."""
        object_in_range = check_dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
            CONSTANTS.OVERTAKE.START_DIST,
            location=Location.opposite(self.blackboard.car_lane),
        )
        if not object_in_range:
            self._start_delay()
            if self._delay_start_time is not None:
                return (
                    time.perf_counter() - self._delay_start_time > self.clac_stay_time()
                )
        else:
            self._delay_start_time = None

        return False

    def _start_delay(self):
        """Delay before starting the state."""
        if self._delay_start_time is None:
            self._delay_start_time = time.perf_counter()
