import copy

from state_machine.components.state_wrapped_sm import StateWrappedStateMachine
from state_machine.states import CONSTANTS
from state_machine.states.drive.driving import DrivingState
from state_machine.states.overtake.ready import ReadyState
from state_machine.states.overtake.stay import StayState
from state_machine.states.overtake.switch_lane import SwitchLaneState
from state_machine.states.overtake.switch_lane_back import SwitchLaneBackState


class OvertakingStateMachine(StateWrappedStateMachine):
    """Overtaking state class."""

    NAME = "overtaking"

    def __init__(self, debug: bool = False):
        """Initializes the OvertakingState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "done": DrivingState.NAME,
            "canceled": DrivingState.NAME,
        }

        # Internal states
        state_classes = [
            ReadyState,
            SwitchLaneState,
            StayState,
            SwitchLaneBackState,
        ]

        super().__init__(state_classes, debug)

    def execute(self, blackboard):
        """Execute the state machine."""
        if self._first_call:
            blackboard["start_location"] = copy.copy(blackboard["car_location"])
        return super().execute(blackboard, timeout_time=CONSTANTS.OVERTAKE.TIMEOUT)
