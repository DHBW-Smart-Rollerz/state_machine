import time

import yasmin

from state_machine.utils import Location


class BaseState(yasmin.State):
    """Default state for Smarty."""

    NAME = "smarty"
    TRANSITIONS = {}

    def __init__(self, debug: bool = False):
        """Initialize the BaseState."""
        super().__init__(outcomes=list(self.TRANSITIONS.keys()))
        self._init_time = time.perf_counter()
        yasmin.YASMIN_LOG_INFO(f"Entering {self.NAME} state")
        self.blackboard: yasmin.Blackboard = None
        self.debug: bool = debug
        self.car_location: Location = Location.UNKNOWN
        self.last_state: object = None
        self.last_state_time_stamp: int = 0
        self.object_list: list[dict] = []
        self.sign_list: list[dict] = []

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Execute the state.

        Arguments:
            blackboard -- Blackboard object
        """
        self.parse_blackboard(blackboard)
        yasmin.YASMIN_LOG_INFO(f"Executing {self.NAME} state")

    def parse_blackboard(self, blackboard: yasmin.Blackboard):
        """
        Parse the blackboard.

        Arguments:
            blackboard -- Blackboard object
        """
        self.blackboard = blackboard
        self.debug: bool = blackboard["debug"]
        self.car_location: Location = blackboard["car_location"]
        self.last_state: object = blackboard["last_state"]
        self.last_state_time_stamp: int = blackboard["last_state_time_stamp"]
        self.object_list: list[dict] = blackboard["object_list"]
        self.sign_list: list[dict] = blackboard["sign_list"]
