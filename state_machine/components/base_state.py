import time

import yasmin
from smarty_utils.enums import Light, Nodes, NodeState

from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.utils import Location


class BaseState(yasmin.State):
    """Default state for Smarty."""

    NAME = "smarty"
    TRANSITIONS = {}
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE,
        max_speed=0.0,
        goal_lane=Location.RIGHT,
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
        self.debug: bool = debug
        self.car_location: Location = Location.UNKNOWN
        self.last_state: object = None
        self.last_state_time_stamp: int = 0
        self.object_list: list[dict] = []
        self.sign_list: list[dict] = []

    def execute(
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
            blackboard.last_state = self.NAME
            blackboard.update(self.STATE_DESCRIPTION)
        yasmin.YASMIN_LOG_INFO(f"Executing {self.NAME} state")
