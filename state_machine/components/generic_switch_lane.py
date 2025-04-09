import copy

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.utils import Location


class GenericSwitchLaneState(BaseState):
    """Switch lane during overtaking."""

    NAME = "switch_lane"
    STATE_DESCRIPTION = StateDescription(
        max_speed=CONSTANTS.MAX_SPEED_SWITCH_LANE,
    )

    def __init__(self, final_state: BaseState | str, debug: bool = False):
        """Initialize the SwitchLaneState."""
        if not isinstance(final_state, str):
            final_state = final_state.NAME

        self.TRANSITIONS = {
            "loop": self.NAME,
            "switch_lane_done": final_state,
        }

        self._start_location = None
        self._first_call = True

        super().__init__(debug)

    def reset(self):
        """Reset the state."""
        self._first_call = True
        self._start_location = None

    def execute(self, blackboard):
        """
        Execute the state.

        Arguments:
            blackboard -- The blackboard containing the state information

        Returns:
            str -- The next state to transition to
        """
        if self._first_call:
            self.STATE_DESCRIPTION = StateDescription(
                max_speed=CONSTANTS.MAX_SPEED_SWITCH_LANE,
                goal_lane=Location.opposite(blackboard["car_location"]),
            )
            self._start_location: Location = copy.copy(blackboard["car_location"])
            self._first_call = False
        super().execute(blackboard)

        # Check if the lane switch is done
        if self.check_lane_switch_done():
            self.reset()
            return "switch_lane_done"

        return "loop"

    def check_lane_switch_done(self):
        """Check if the lane switch is done."""
        if self.car_location != self._start_location:
            return True
