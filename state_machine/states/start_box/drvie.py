import time

from smarty_utils.enums import Location

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS


class DriveState(BaseState):
    """Ready to start state."""

    NAME = "startbox-drive"
    STATE_DESCRIPTION = StateDescription(
        goal_lane=Location.RIGHT_LANE,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {"next": "done"}
        super().__init__(debug)

    def local_execute(self) -> str:
        """Execute the ReadyState."""
        super().local_execute()
        start = time.perf_counter()

        while time.perf_counter() - start < CONSTANTS.START_BOX.DRIVE_TIMEOUT:
            self.blackboard.drive_straight = True
            self.log_state("Start Box: Driving straight")
            time.sleep(0.0001)

        self.blackboard.drive_straight = False
        self.log_state("Start Box: Drive timeout reached, stopping")
        return "next"
