import copy

from state_machine.components.state_description import BlackBoard
from state_machine.components.state_wrapped_sm import StateWrappedStateMachine
from state_machine.states import CONSTANTS
from state_machine.states.cross_walk.approach import ApproachCrosswalk
from state_machine.states.cross_walk.detect_pedestrian import DetectPedestrian
from state_machine.states.cross_walk.ready import ReadyState
from state_machine.states.cross_walk.wait import WaitState
from state_machine.states.drive.driving import DrivingState


class CrosswalkStateMachine(StateWrappedStateMachine):
    """Crosswalk state."""

    NAME = "crosswalk"

    def __init__(self, debug: bool = False):
        """Initializes the CrosswalkState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "done": DrivingState.NAME,
            "canceled": DrivingState.NAME,
        }
        # Internal states
        state_classes = [ReadyState, DetectPedestrian, WaitState, ApproachCrosswalk]

        super().__init__(state_classes, debug)

    def local_execute(self):
        """Execute the state machine."""
        if self._first_call:
            self.blackboard.start_location = copy.copy(self.blackboard.car_lane)
        return super().local_execute(timeout_time=CONSTANTS.CROSS_WALK.TIMEOUT)
