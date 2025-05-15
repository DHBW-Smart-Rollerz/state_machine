import copy

from state_machine.components.state_description import BlackBoard
from state_machine.components.state_wrapped_sm import StateWrappedStateMachine
from state_machine.states import CONSTANTS
from state_machine.states.barred_area.approach import ApproachBarredArea
from state_machine.states.barred_area.detect_obstacle import DetectObstacleState
from state_machine.states.barred_area.ready import ReadyState
from state_machine.states.barred_area.stay import StayState
from state_machine.states.barred_area.switch_lane import (
    SwitchLaneBackState,
    SwitchLaneState,
)
from state_machine.states.barred_area.wait import WaitState
from state_machine.states.drive.driving import DrivingState


class BarredAreaState(StateWrappedStateMachine):
    """Barred area state."""

    NAME = "barred-area"

    def __init__(self, debug: bool = False):
        """Initializes the CrosswalkState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "done": DrivingState.NAME,
            "canceled": DrivingState.NAME,
        }
        # Internal states
        state_classes = [
            ReadyState,
            ApproachBarredArea,
            DetectObstacleState,
            WaitState,
            SwitchLaneState,
            StayState,
            SwitchLaneBackState,
        ]

        super().__init__(state_classes, debug)

    def local_execute(self, blackboard: BlackBoard):
        """Execute the state machine."""
        if self._first_call:
            blackboard["start_location"] = copy.copy(blackboard.car_lane)
        return super().local_execute(
            blackboard, timeout_time=CONSTANTS.BARRED_AREA.TIMEOUT
        )
