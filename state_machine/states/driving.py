import yasmin

from state_machine.states import (
    BarredAreaState,
    CrosswalkState,
    ExpressWayState,
    IntersectionState,
    NoPassingZoneState,
    OvertakingState,
    ParkingState,
)


class DrivingState(yasmin.State):
    NAME = "driving"
    TRANSITIONS = {
        "driving": NAME,
        "approaching_obstacle": OvertakingState.NAME,
        "approaching_intersection": IntersectionState.NAME,
        "approaching_parking_area": ParkingState.NAME,
        "approaching_barred_area": BarredAreaState.NAME,
        "approaching_crosswalk": CrosswalkState.NAME,
        "approaching_express_way": ExpressWayState.NAME,
        "approaching_no_passing_zone": NoPassingZoneState.NAME,
    }

    def __init__(self):
        super().__init__(outcomes=[])
        self.get_logger().info(f"Entering {self.NAME} state")

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        self.get_logger().info(f"Executing {self.NAME} state")

        if self._is_approaching_obstacle(blackboard):
            return "approaching_obstacle"
        elif self._is_approaching_intersection(blackboard):
            return "approaching_intersection"
        elif self._is_approaching_parking_area(blackboard):
            return "approaching_parking_area"
        elif self._is_approaching_barred_area(blackboard):
            return "approaching_barred_area"
        elif self._is_approching_crosswalk(blackboard):
            return "approaching_crosswalk"
        elif self._is_approching_express_way(blackboard):
            return "approaching_express_way"
        elif self._is_approaching_no_passing_zone(blackboard):
            return "approaching_no_passing_zone"
        else:
            return "driving"

    def _is_approaching_obstacle(self, blackboard: yasmin.Blackboard) -> bool:
        # obstacle in right land
        # and distance to obstacle < 50cm
        # and (no no-passing sign detected or no-passing sign distance > 200cm)
        pass

    def _is_approaching_intersection(self, blackboard: yasmin.Blackboard) -> bool:
        # stop sign distance < 50cm
        # or yield sign distance < 50cm
        pass

    def _is_approaching_parking_area(self, blackboard: yasmin.Blackboard) -> bool:
        # parking area distance < 50cm
        pass

    def _is_approaching_barred_area(self, blackboard: yasmin.Blackboard) -> bool:
        # barred area distance < 50cm
        pass

    def _is_approching_crosswalk(self, blackboard: yasmin.Blackboard) -> bool:
        # crosswalk distance < 50cm
        pass

    def _is_approching_express_way(self, blackboard: yasmin.Blackboard) -> bool:
        # express way distance < 50cm
        pass

    def _is_approaching_no_passing_zone(self, blackboard: yasmin.Blackboard) -> bool:
        # no passing zone distance < 50cm
        pass
