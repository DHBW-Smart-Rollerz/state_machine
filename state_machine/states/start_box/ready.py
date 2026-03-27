import copy
import time

import yasmin
from smarty_utils.enums import SIGNS, Light, Location, Nodes, NodeState

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.utils import detectors


class ReadyState(BaseState):
    """Ready to start state."""

    NAME = "startbox-ready"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=0.0,
        goal_lane=Location.RIGHT_LANE,
        node_states={
            Nodes.OBJECT_DETECTION: NodeState.ACTIVE,
            Nodes.LANE_DETECTION: NodeState.ACTIVE,
            Nodes.PATH_PLANNING: NodeState.ACTIVE,
            Nodes.CONTROL: NodeState.ACTIVE,
            Nodes.STATE_ESTIMATION: NodeState.ACTIVE,
        },
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {"start_box_open": "done"}
        super().__init__()

    def local_execute(self, blackboard: BlackBoard) -> str:
        """
        Execute the ReadyState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- name of the next state
        """
        super().local_execute(blackboard)

        while self._is_start_box_open(self.blackboard):
            self.log_state("Start Box: Waiting for start box to be open")
            time.sleep(0.0001)
        return "start_box_open"

    def _is_start_box_open(self, blackboard: BlackBoard) -> bool:
        """
        Check if the startbox is open.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            bool -- True if the startbox is open, False otherwise
        """
        # return True
        # Stop sign in sign list
        signs: list[dict] = copy.copy(blackboard.signs)

        sign_dist_thresh = CONSTANTS.START_BOX.DISTANCE_THRESH
        timeout = CONSTANTS.START_BOX.READY_TIMEOUT
        detected = detectors.check_dist_to_obj_sign(
            signs, SIGNS.STOP, sign_dist_thresh, Location.NOT_RELEVANT
        )
        current_time = time.perf_counter()

        if current_time - self._init_time > timeout:
            yasmin.YASMIN_LOG_WARN(
                f"Start Box open timeout after {current_time - self._init_time} seconds"
            )
            return False

        return detected
