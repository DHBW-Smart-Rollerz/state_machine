import yasmin


class ParkingState(yasmin.State):
    NAME = "parking"
    TRANSITIONS = {}

    def __init__(self):
        super().__init__(outcomes=[])
        self.get_logger().info(f"Entering {self.NAME} state")

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        self.get_logger().info(f"Executing {self.NAME} state")
