import time

import yasmin
from smarty_utils.enums import (
    OBJECTS,
    SIGNS,
    Light,
    Location,
    Nodes,
    NodeState,
    StateMachineTestModes,
)

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.utils.detectors import check_dist_to_obj_sign


class DrivingState(BaseState):
    """Driving state."""

    NAME = "driving"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.DRIVE.MAX_SPEED,
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
        """Initialize the DrivingState."""
        # Required (Circular Import)
        from state_machine.states.barred_area.barred_area import BarredAreaState
        from state_machine.states.cross_walk.crosswalk import CrosswalkStateMachine
        from state_machine.states.intersection.express_way import ExpressWayState
        from state_machine.states.intersection.intersection import (
            IntersectionStateMachine,
        )
        from state_machine.states.no_passing_zone.no_passing_zone import (
            NoPassingZoneState,
        )
        from state_machine.states.overtake.overtaking import OvertakingStateMachine
        from state_machine.states.parking import ParkingState

        self.TRANSITIONS = {
            "approaching_obstacle": OvertakingStateMachine.NAME,
            "approaching_intersection": IntersectionStateMachine.NAME,
            "approaching_parking_area": ParkingState.NAME,
            "approaching_barred_area": BarredAreaState.NAME,
            "approaching_crosswalk": CrosswalkStateMachine.NAME,
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

    def local_execute(self) -> str:
        """Execute the DrivingState."""
        super().local_execute()

        while True:
            if self.blackboard.remote_state == 1:  # Free drive
                self.log_state("Free drive")
                time.sleep(0.0001)
                continue

            if (
                self._is_approaching_intersection()
                and self._check_last_state(self.TRANSITIONS["approaching_intersection"])
                and not self._check_test_mode(StateMachineTestModes.NO_INTERSECTION)
            ):
                return "approaching_intersection"
            # elif self._is_approaching_parking_area() and self._check_last_state(
            #     self.TRANSITIONS["approaching_parking_area"]
            # ):
            #     return "approaching_parking_area"
            elif (
                self._is_approaching_barred_area()
                and self._check_last_state(self.TRANSITIONS["approaching_barred_area"])
                and not self._check_test_mode(StateMachineTestModes.NO_BARRED_AREA)
            ):
                return "approaching_barred_area"
            elif (
                self._is_approaching_crosswalk()
                and self._check_last_state(self.TRANSITIONS["approaching_crosswalk"])
                and not self._check_test_mode(StateMachineTestModes.NO_CROSSWALK)
            ):
                return "approaching_crosswalk"
            # elif self._is_approaching_express_way() and self._check_last_state(
            #     self.TRANSITIONS["approaching_express_way"]
            # ):
            #     return "approaching_express_way"
            elif (
                self._is_approaching_no_passing_zone()
                and self._check_last_state(
                    self.TRANSITIONS["approaching_no_passing_zone"]
                )
                and not self._check_test_mode(StateMachineTestModes.NO_NO_PASSING_ZONE)
            ):
                return "approaching_no_passing_zone"
            elif (
                self._is_approaching_obstacle()
                and self._check_last_state(self.TRANSITIONS["approaching_obstacle"])
                and not self._check_test_mode(StateMachineTestModes.NO_OVERTAKING)
            ):
                return "approaching_obstacle"
            self.log_state("Driving normally")
            time.sleep(0.0001)

    def _check_last_state(self, state: str) -> bool:
        """
        Check if the last state was the given state.

        Arguments:
            state -- The state to check

        Returns:
            bool -- True if the last state was the given state, False otherwise
        """
        return not (
            self.blackboard.last_state == state
            and time.perf_counter() - self.blackboard.last_timestamp
            < CONSTANTS.DRIVE.STATE_TIMEOUT
        )

    def _is_approaching_obstacle(self) -> bool:
        return check_dist_to_obj_sign(
            self.blackboard.objects,
            OBJECTS.VEHICLE,
            CONSTANTS.DRIVE.OVERTAKING_THRESHOLD,
            location=self.blackboard.car_lane,
        ) and not check_dist_to_obj_sign(
            self.blackboard.signs,
            [SIGNS.STOP, SIGNS.GIVE_WAY],
            CONSTANTS.DRIVE.INTERSECTION_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_intersection(
        self,
    ) -> bool:
        return check_dist_to_obj_sign(
            self.blackboard.signs,
            [SIGNS.STOP, SIGNS.GIVE_WAY],
            CONSTANTS.DRIVE.INTERSECTION_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_parking_area(self) -> bool:
        return check_dist_to_obj_sign(
            self.blackboard.signs,
            [SIGNS.PARKING],
            CONSTANTS.DRIVE.PARKING_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_barred_area(self) -> bool:
        return check_dist_to_obj_sign(
            self.blackboard.signs,
            [SIGNS.PRIORITY_ONCOMING_TRAFFIC],
            CONSTANTS.DRIVE.BARRED_AREA_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_crosswalk(self) -> bool:
        return check_dist_to_obj_sign(
            self.blackboard.signs,
            [SIGNS.CROSSWALK],
            CONSTANTS.DRIVE.CROSSWALK_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_express_way(self) -> bool:
        return check_dist_to_obj_sign(
            self.blackboard.signs,
            [SIGNS.FAST_TRACK, SIGNS.FAST_TRACK_LIFTED],
            CONSTANTS.DRIVE.EXPRESS_WAY_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _is_approaching_no_passing_zone(self) -> bool:
        return check_dist_to_obj_sign(
            self.blackboard.signs,
            [SIGNS.NO_OVERTAKING, SIGNS.NO_OVERTAKING_LIFTED],
            CONSTANTS.DRIVE.NO_PASSING_ZONE_THRESHOLD,
            location=Location.NOT_RELEVANT,
        )

    def _check_test_mode(self, mode: StateMachineTestModes) -> bool:
        """Check if the current test mode is the given mode."""
        return StateMachineTestModes.use(self.blackboard.test_mode, mode)
