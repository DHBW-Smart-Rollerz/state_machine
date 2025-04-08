import yasmin

from state_machine.components.base_state import BaseState
from state_machine.utils import Location
from state_machine.utils.detectors import check_dist_to_obj_sign


class DrivingState(BaseState):
    """Driving state."""

    NAME = "driving"

    def __init__(self, debug: bool = False):
        """Initialize the DrivingState."""
        # REQUIRED (Circular import)
        from state_machine.states.barred_area import BarredAreaState
        from state_machine.states.crosswalk import CrosswalkState
        from state_machine.states.express_way import ExpressWayState
        from state_machine.states.intersection import IntersectionState
        from state_machine.states.no_passing_zone import NoPassingZoneState
        from state_machine.states.overtaking import OvertakingState
        from state_machine.states.parking import ParkingState

        self.TRANSITIONS = {
            "loop": self.NAME,
            "approaching_obstacle": OvertakingState.NAME,
            "approaching_intersection": IntersectionState.NAME,
            "approaching_parking_area": ParkingState.NAME,
            "approaching_barred_area": BarredAreaState.NAME,
            "approaching_crosswalk": CrosswalkState.NAME,
            "approaching_express_way": ExpressWayState.NAME,
            "approaching_no_passing_zone": NoPassingZoneState.NAME,
            "canceled": "canceled",
            "done": "done",
        }
        super().__init__()

    def start_nodes(self) -> list:
        """
        Start nodes for the DrivingState.

        Returns:
            list -- list of started nodes
        """
        return []

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Execute the DrivingState.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- name of the next state
        """
        super().execute(blackboard)

        if self._is_approaching_obstacle():
            return "approaching_obstacle"
        elif self._is_approaching_intersection():
            return "approaching_intersection"
        elif self._is_approaching_parking_area():
            return "approaching_parking_area"
        elif self._is_approaching_barred_area():
            return "approaching_barred_area"
        elif self._is_approaching_crosswalk():
            return "approaching_crosswalk"
        elif self._is_approaching_express_way():
            return "approaching_express_way"
        elif self._is_approaching_no_passing_zone():
            return "approaching_no_passing_zone"
        else:
            return "loop"

    def _is_approaching_obstacle(self) -> bool:
        from state_machine.states import CONSTANTS

        return check_dist_to_obj_sign(
            self.object_list,
            ["vehicle"],
            CONSTANTS.DRIVE.OVERTAKING_THRESHOLD,
            location=self.car_location,
        )

    def _is_approaching_intersection(
        self,
    ) -> bool:
        from state_machine.states import CONSTANTS

        return check_dist_to_obj_sign(
            self.object_list,
            ["stop", "give_way", "priority_oncoming_traffic"],
            CONSTANTS.DRIVE.INTERSECTION_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_parking_area(self) -> bool:
        from state_machine.states import CONSTANTS

        return check_dist_to_obj_sign(
            self.object_list,
            ["parking"],
            CONSTANTS.DRIVE.PARKING_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_barred_area(self) -> bool:
        # TODO: Object not implemented yet
        pass

    def _is_approaching_crosswalk(self) -> bool:
        from state_machine.states import CONSTANTS

        return check_dist_to_obj_sign(
            self.object_list,
            ["crosswalk"],
            CONSTANTS.DRIVE.CROSSWALK_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_express_way(self) -> bool:
        from state_machine.states import CONSTANTS

        return check_dist_to_obj_sign(
            self.object_list,
            ["fast_track", "fast_track_lifted"],
            CONSTANTS.DRIVE.EXPRESS_WAY_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_no_passing_zone(self) -> bool:
        from state_machine.states import CONSTANTS

        return check_dist_to_obj_sign(
            self.object_list,
            ["no_overtaking", "no_overtaking_lifted"],
            CONSTANTS.DRIVE.NO_PASSING_ZONE_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )
