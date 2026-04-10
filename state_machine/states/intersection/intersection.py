import copy

from state_machine.components.state_description import BlackBoard
from state_machine.components.state_wrapped_sm import StateWrappedStateMachine
from state_machine.states import CONSTANTS
from state_machine.states.drive.driving import DrivingState
from state_machine.states.intersection.approach import ApproachGiveWay, ApproachStop
from state_machine.states.intersection.give_way import GiveWayState
from state_machine.states.intersection.ready import ReadyState
from state_machine.states.intersection.stop import StopState
from state_machine.states.intersection.wait import WaitState


class IntersectionStateMachine(StateWrappedStateMachine):
    """Intersection state class."""

    NAME = "intersection"

    def __init__(self, debug: bool = False):
        """Initializes the IntersectionStateMachine."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "done": DrivingState.NAME,
            "canceled": DrivingState.NAME,
        }

        # Internal states
        state_classes = [
            ReadyState,
            StopState,
            GiveWayState,
            WaitState,
            ApproachStop,
            ApproachGiveWay,
        ]

        super().__init__(state_classes, debug)

    def local_execute(self):
        """Execute the state machine."""
        if self._first_call:
            self.blackboard.start_location = copy.copy(self.blackboard.car_lane)
        return super().local_execute(timeout_time=CONSTANTS.INTERSECTION.TIMEOUT)
