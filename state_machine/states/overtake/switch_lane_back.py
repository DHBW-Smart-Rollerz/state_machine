from state_machine.components.base_state import BaseState


class SwitchLaneBackState(BaseState):
    """Switch lane back after overtaking."""

    NAME = "switch_lane_back"

    def __init__(self, debug: bool = False):
        """Initialize the SwitchLaneBackState."""
        self.TRANSITIONS = {
            "loop": self.NAME,
            "switch_lane_done": "done",
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
        if self.check_lane_switch_done():
            return "switch_lane_done"

        return "loop"
