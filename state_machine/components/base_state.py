import time

import yasmin
from smarty_utils.enums import Light, Location, Nodes, NodeState

from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS


class BaseState(yasmin.State):
    """Default state for Smarty."""

    NAME = "smarty"
    TRANSITIONS = {}
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE_NORMAL,
        max_speed=0.0,
        goal_lane=Location.RIGHT_LANE,
        node_states={
            Nodes.OBJECT_DETECTION: NodeState.INACTIVE,
            Nodes.LANE_DETECTION: NodeState.INACTIVE,
            Nodes.PATH_PLANNING: NodeState.INACTIVE,
            Nodes.CONTROL: NodeState.INACTIVE,
            Nodes.STATE_ESTIMATION: NodeState.INACTIVE,
        },
    )

    def __init__(self, debug: bool = False):
        """Initialize the BaseState."""
        super().__init__(outcomes=list(self.TRANSITIONS.keys()))
        self._init_time = time.perf_counter()
        yasmin.YASMIN_LOG_INFO(f"Entering {self.NAME} state")
        self.blackboard: BlackBoard = None
        self.last_log_time: float = 0

    def local_execute(
        self,
        blackboard: BlackBoard,
        update_black_board: bool = True,
    ) -> str:
        """
        Execute the state.

        Arguments:
            blackboard -- Blackboard object
        """
        if update_black_board:
            blackboard.update(self.STATE_DESCRIPTION)
            blackboard._current_state = self.NAME
        yasmin.YASMIN_LOG_INFO(f"Executing {self.NAME} state")
        self.blackboard = blackboard
        time.sleep(0.0001)

    def execute(
        self,
        blackboard: BlackBoard,
    ):
        """
        Execute the state.

        Arguments:
            blackboard -- Blackboard object
        """
        output = self.local_execute(blackboard)
        self.set_last_state()
        return output

    def set_last_state(self, other_state: str = ""):
        """Set the last state."""
        if other_state:
            self.blackboard.last_state = other_state
        else:
            self.blackboard.last_state = self.NAME

    def log_state(self, message: str):
        """Log info message."""
        if int(time.perf_counter() - self.last_log_time) > CONSTANTS.LOG_TIME:
            yasmin.YASMIN_LOG_INFO(f"{self.NAME} - {message}")
            self.last_log_time = time.perf_counter()
