import time

from smarty_utils.enums import Light, Location, Nodes

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS


class GenericSwitchLaneState(BaseState):
    """Switch lane during overtaking."""

    NAME = "switch_lane"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
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

    def local_execute(self, blackboard: BlackBoard):
        """
        Execute the state.

        Arguments:
            blackboard -- The blackboard containing the state information

        Returns:
            str -- The next state to transition to
        """
        goal_lane = Location.opposite(blackboard.car_lane)
        self.STATE_DESCRIPTION = BlackBoard(
            max_speed=CONSTANTS.MAX_SPEED_SWITCH_LANE,
            goal_lane=goal_lane,
            light_configuration=(
                Light.BLINK_LEFT if goal_lane == Location.LEFT else Light.BLINK_RIGHT
            ),
            node_states={
                Nodes.OBJECT_DETECTION: Nodes.ACTIVE,
                Nodes.LANE_DETECTION: Nodes.ACTIVE,
                Nodes.PATH_PLANNING: Nodes.ACTIVE,
                Nodes.CONTROL: Nodes.ACTIVE,
                Nodes.STATE_ESTIMATION: Nodes.ACTIVE,
            },
        )
        self._start_location: Location = blackboard.car_lane
        self._first_call = False
        super().local_execute(blackboard)

        # Check if the lane switch is done
        while not self.check_lane_switch_done():
            # Check if the lane switch is done
            self.reset()
            self.log_state("Switch Lane: Waiting for lane switch to be done")
            time.sleep(0.0001)
        return "switch_lane_done"

    def check_lane_switch_done(self):
        """Check if the lane switch is done."""
        if self.car_location != self._start_location:
            return True
