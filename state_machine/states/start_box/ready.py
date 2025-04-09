import time

import yasmin

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import (
    Light,
    Nodes,
    NodesModes,
    StateDescription,
)
from state_machine.states import CONSTANTS
from state_machine.utils import Location, detectors


class ReadyState(BaseState):
    """Ready to start state."""

    NAME = "ready"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=0.0,
        goal_lane=Location.RIGHT,
        node_modes={
            Nodes.OBJECT_DETECTION: NodesModes.ACTIVE,
            Nodes.LANE_DETECTION: NodesModes.ACTIVE,
            Nodes.PATH_PLANNING: NodesModes.ACTIVE,
            Nodes.CONTROL: NodesModes.ACTIVE,
            Nodes.STATE_ESTIMATION: NodesModes.ACTIVE,
        },
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {"loop": self.NAME, "start_box_open": "done"}
        super().__init__()

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Execute the ReadyState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- name of the next state
        """
        super().execute(blackboard)

        if self._is_start_box_open(blackboard):
            return "start_box_open"
        else:
            return "loop"

    def _is_start_box_open(self, blackboard: yasmin.Blackboard) -> bool:
        """
        Check if the startbox is open.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            bool -- True if the startbox is open, False otherwise
        """
        return True
        # Stop sign in sign list
        signs: list[dict] = blackboard.get("sign_list")

        sign_dist_thresh = CONSTANTS.START_BOX.DISTANCE_THRESH
        timeout = CONSTANTS.START_BOX.READY_TIMEOUT
        detected = detectors.check_dist_to_obj_sign(
            signs, "stop", sign_dist_thresh, Location.NOT_RELEVANT
        )
        current_time = time.perf_counter()

        if current_time - self._init_time > timeout:
            yasmin.YASMIN_LOG_WARN(
                f"Start Box open timeout after {current_time - self._init_time} seconds"
            )
            return True

        return not detected
