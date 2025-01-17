import yasmin


class SmartyState(yasmin.State):
    """Default state for Smarty."""

    NAME = "smarty"
    TRANSITIONS = {}

    def __init__(self):
        """Initialize the state."""
        super().__init__(outcomes=list(self.TRANSITIONS.keys()))
        yasmin.YASMIN_LOG_INFO(f"Entering {self.NAME} state")

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Execute the state.

        Arguments:
            blackboard -- Blackboard object
        """
        yasmin.YASMIN_LOG_INFO(f"Executing {self.NAME} state")
