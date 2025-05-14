import time

from smarty_utils.enums import Light

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription


class Approach(BaseState):
    """Handling approaching intersection."""

    NAME = "approach"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL, max_speed=0.1
    )
    APPROACH_DISTANCE = 300  # mm

    def __init__(self, next_state: str, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "next": next_state,
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

        time_to_wait = (self.APPROACH_DISTANCE / 1000) / self.blackboard.max_speed
        while time.perf_counter() - start_time <= time_to_wait:
            time.sleep(0.0001)

            self.log_state(
                f"{self.NAME}: Approaching - {time_to_wait - (time.perf_counter() - start_time):.2f} seconds left"
            )
        return "next"
