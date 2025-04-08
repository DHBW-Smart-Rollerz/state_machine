import copy

from state_machine.components.state_wrapped_sm import StateWrappedStateMachine


class OvertakingStateMachine(StateWrappedStateMachine):
    """Overtaking state class."""

    NAME = "overtaking"

    def __init__(self, debug: bool = False):
        """Initializes the OvertakingState."""
        # REQUIRED (Circular import)
        from state_machine.states import overtake
        from state_machine.states.drive.driving import DrivingState

        self.TRANSITIONS = {
            "loop": self.NAME,
            "done": DrivingState.NAME,
            "canceled": DrivingState.NAME,
        }

        # Internal states
        state_classes = [
            overtake.ReadyState,
            overtake.SwitchLaneState,
            overtake.StayState,
            overtake.SwitchLaneBackState,
        ]

        super().__init__(state_classes, debug)

    def execute(self, blackboard):
        """Execute the state machine."""
        from state_machine.states import CONSTANTS

        if self._first_call:
            blackboard["start_location"] = copy.copy(blackboard["car_location"])
        return super().execute(blackboard, timeout_time=CONSTANTS.OVERTAKE.TIMEOUT)
