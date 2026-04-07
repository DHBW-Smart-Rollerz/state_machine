import time

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.barred_area.switch_lane import SwitchLaneBackState


class StayState(BaseState):
    """Stay in the lane during barred area."""

    NAME = "barred-area-stay"
    STATE_DESCRIPTION = StateDescription(
        max_speed=CONSTANTS.BARRED_AREA.MAX_SPEED,
    )

    def __init__(self, debug: bool = False):
        """Initialize the StayState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "area_done": SwitchLaneBackState.NAME,
        }
        super().__init__(debug)
        self._delay_start_time = None
        self._rest_time = 0.0

    def local_execute(self):
        """Execute the state."""
        super().local_execute()

        # Check if the barred area is done
        while not self.check_area_done():
            self.log_state(
                f"Barred Area: Waiting for barred area to be done {self._rest_time} left"
            )

            time.sleep(0.0001)

        return "area_done"

    def calc_stay_time(self):
        """Calculate the time to stay in the lane after barred area."""
        return (CONSTANTS.BARRED_AREA.STAY_DISTANCE / 1000) / self.blackboard.max_speed

    def check_area_done(self):
        """Check if the barred area is done."""
        if self._delay_start_time is None:
            self._delay_start_time = time.perf_counter()
        else:
            self._rest_time = self.calc_stay_time() - (
                time.perf_counter() - self._delay_start_time
            )
            return self._rest_time <= 0
        return False
