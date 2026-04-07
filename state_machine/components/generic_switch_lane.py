import time

import rclpy
import rclpy.logging
from smarty_utils.enums import Light, Location, Nodes, NodeState

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

        self._goal_lane = None

        super().__init__(debug)

    def local_execute(self):
        """Execute the state."""
        self._goal_lane = Location.opposite(self.blackboard.car_lane)
        self.STATE_DESCRIPTION = StateDescription(
            max_speed=CONSTANTS.MAX_SPEED_SWITCH_LANE,
            goal_lane=self._goal_lane,
            light_configuration=(
                Light.BLINK_LEFT_NORMAL
                if self._goal_lane == Location.LEFT_LANE
                else Light.BLINK_RIGHT_NORMAL
            ),
            node_states={
                Nodes.OBJECT_DETECTION: NodeState.ACTIVE,
                Nodes.LANE_DETECTION: NodeState.ACTIVE,
                Nodes.PATH_PLANNING: NodeState.ACTIVE,
                Nodes.CONTROL: NodeState.ACTIVE,
                Nodes.STATE_ESTIMATION: NodeState.ACTIVE,
            },
        )
        super().local_execute()

        # Check if the lane switch is done
        while not self.check_lane_switch_done():
            # Check if the lane switch is done
            self.log_state("Switch Lane: Waiting for lane switch to be done")
            time.sleep(0.0001)
        return "switch_lane_done"

    def check_lane_switch_done(self):
        """Check if the lane switch is done."""
        rclpy.logging.get_logger("state_machine").info(
            f"Switch Lane: Lane switch done. Start location: {self._goal_lane}, Current location: {self.blackboard.car_lane}"
        )
        if self.blackboard.car_lane == self._goal_lane:
            return True
