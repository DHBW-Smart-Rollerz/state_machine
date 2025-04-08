from state_machine.components.base_state import BaseState
from state_machine.utils import Location


class SwitchLaneState(BaseState):
    """Switch lane during overtaking."""

    NAME = "switch_lane"

    def __init__(self, debug: bool = False):
        """Initialize the SwitchLaneState."""
        from state_machine.states import overtake

        self.TRANSITIONS = {
            "loop": self.NAME,
            "switch_lane_done": overtake.StayState.NAME,
        }

        # TODO: Publish the lane change command

        super().__init__(debug)

    def execute(self, blackboard):
        """
        Execute the state.

        Arguments:
            blackboard -- The blackboard containing the state information

        Returns:
            str -- The next state to transition to
        """
        super().execute(blackboard)

        # Check if the lane switch is done
        if self.check_lane_switch_done(blackboard["start_location"]):
            return "switch_lane_done"

        return "loop"

    def check_lane_switch_done(self, start_location: Location):
        """Check if the lane switch is done."""
        if self.car_location != start_location:
            return True
