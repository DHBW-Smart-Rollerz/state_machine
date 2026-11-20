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
        last_sign = None

        while time.perf_counter() - start < CONSTANTS.INTERSECTION.READY_TIMEOUT:
            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.STOP],
                CONSTANTS.INTERSECTION.START_DIST,
            ):
                return (
                    "start_crossing_stop"
                    if self.blackboard.use_crossing_detection
                    else "start_stop"
                )

            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.GIVE_WAY],
                CONSTANTS.INTERSECTION.GIVE_WAY_DIST,
            ):
                return (
                    "start_crossing_give_way"
                    if self.blackboard.use_crossing_detection
                    else "start_give_way"
                )

            # Remember which sign we saw while approaching, so that a sign
            # leaving the camera's field of view does not skip the stop.
            for sign in (SIGNS.STOP, SIGNS.GIVE_WAY):
                if check_dist_to_obj_sign(
                    self.blackboard.signs,
                    [sign],
                    DRIVE_CONSTANTS.INTERSECTION_THRESHOLD,
                ):
                    last_sign = sign

            # Neither sign visible at drive threshold
            if not check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.STOP, SIGNS.GIVE_WAY],
                DRIVE_CONSTANTS.INTERSECTION_THRESHOLD,
            ):
                if last_sign is not None:
                    # The sign was seen before and is now too close/out of view:
                    # we are at the intersection, so start the approach/stop.
                    yasmin.YASMIN_LOG_WARN(
                        f"Intersection: {last_sign} left view, starting approach"
                    )
                    if last_sign == SIGNS.STOP:
                        return (
                            "start_crossing_stop"
                            if self.blackboard.use_crossing_detection
                            else "start_stop"
                        )
                    return (
                        "start_crossing_give_way"
                        if self.blackboard.use_crossing_detection
                        else "start_give_way"
                    )
                yasmin.YASMIN_LOG_WARN(
                    f"Intersection: sign lost, assuming zone passed — skipping, has signs: {self.blackboard.signs}"
                )
                return "canceled"

            self.log_state("Intersection: Searching for sign")

            time.sleep(0.0001)

        return "canceled"
