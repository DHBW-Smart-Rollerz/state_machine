from state_machine.components.base_state import BaseState
from state_machine.utils.detectors import check_dist_to_obj_sign


class ReadyState(BaseState):
    """Ready for starting the overtaking."""

    NAME = "ready"

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        from state_machine.states import overtake

        self.TRANSITIONS = {
            "loop": self.NAME,
            "start_overtake": overtake.SwitchLaneState.NAME,
        }

        # TODO: Publish lower speed command

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

        from state_machine.states import CONSTANTS

        if check_dist_to_obj_sign(
            self.object_list,
            ["vehicle"],
            CONSTANTS.OVERTAKE.START_DIST,
            location=self.car_location,
        ):
            return "start_overtake"

        return "loop"
