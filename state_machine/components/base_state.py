import time

import yasmin


class BaseState(yasmin.State):
    """Default state for Smarty."""

    NAME = "smarty"
    TRANSITIONS = {}

    def __init__(self):
        """Initialize the BaseState."""
        super().__init__(outcomes=list(self.TRANSITIONS.keys()))
        self._init_time = time.perf_counter()
        yasmin.YASMIN_LOG_INFO(f"Entering {self.NAME} state")

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Execute the state.

        Arguments:
            blackboard -- Blackboard object
        """
        yasmin.YASMIN_LOG_INFO(f"Executing {self.NAME} state")
