import time

import yasmin
from smarty_utils.enums import SIGNS, Light, Nodes, NodeState

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.drive import DRIVE_CONSTANTS
from state_machine.states.intersection.approach import (
    ApproachGiveWay,
    ApproachGiveWayCrossing,
    ApproachStop,
    ApproachStopCrossing,
)
from state_machine.utils.detectors import check_dist_to_obj_sign


class ReadyState(BaseState):
    """Ready for starting the overtaking."""

    NAME = "intersection-ready"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.INTERSECTION.MAX_SPEED,
        node_states={
            Nodes.OBJECT_DETECTION: NodeState.ACTIVE,
            Nodes.LANE_DETECTION: NodeState.ACTIVE,
            Nodes.PATH_PLANNING: NodeState.ACTIVE,
            Nodes.CONTROL: NodeState.ACTIVE,
            Nodes.STATE_ESTIMATION: NodeState.ACTIVE,
            Nodes.CROSSING_DETECTION: NodeState.ACTIVE,
        },
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "start_stop": ApproachStop.NAME,
            "start_give_way": ApproachGiveWay.NAME,
            "start_crossing_stop": ApproachStopCrossing.NAME,
            "start_crossing_give_way": ApproachGiveWayCrossing.NAME,
            "canceled": "canceled",
        }
        super().__init__(debug)

    def local_execute(self):
        """Execute the state."""
        super().local_execute()
        start = time.perf_counter()

        while time.perf_counter() - start < CONSTANTS.INTERSECTION.READY_TIMEOUT:
            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.STOP],
                CONSTANTS.INTERSECTION.START_DIST,
            ):
                return (
                    "start_stop"
                    if self.blackboard.use_crossing_detection
                    else "start_crossing_stop"
                )

            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.GIVE_WAY],
                CONSTANTS.INTERSECTION.GIVE_WAY_DIST,
            ):
                return (
                    "start_give_way"
                    if self.blackboard.use_crossing_detection
                    else "start_crossing_give_way"
                )

            # Neither sign visible at drive threshold — assume already past the
            # intersection, skip back to driving
            if not check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.STOP, SIGNS.GIVE_WAY],
                DRIVE_CONSTANTS.INTERSECTION_THRESHOLD,
            ):
                yasmin.YASMIN_LOG_WARN(
                    f"Intersection: sign lost, assuming zone passed — skipping, has signs: {self.blackboard.signs}"
                )

                return "canceled"

            self.log_state("Intersection: Searching for sign")

            time.sleep(0.0001)

        return "canceled"
