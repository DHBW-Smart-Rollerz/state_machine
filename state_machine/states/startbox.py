import yasmin

from state_machine.states import DrivingState


class StartboxState(yasmin.State):
    NAME = "startbox"
    TRANSITIONS = {
        "startbox_closed": NAME,
        "startbox_open": DrivingState.NAME,
    }

    def __init__(self):
        super().__init__(outcomes=[])
        self.get_logger().info(f"Entering {self.NAME} state")

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        self.get_logger().info(f"Executing {self.NAME} state")

        if self._is_startbox_open(blackboard):
            return "startbox_open"
        else:
            return "startbox_closed"

    def _is_startbox_open(self, blackboard: yasmin.Blackboard) -> bool:
        # stop sign not detected 
        # or stop sign distance > 50cm
        pass
