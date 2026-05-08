import time

from smarty_utils.enums import CrossingLineType, Light

from state_machine.components.approach import Approach
from state_machine.components.base_state import BaseState
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.intersection.give_way import GiveWayState
from state_machine.states.intersection.stop import StopState
from state_machine.utils.detectors import get_distance_to_line


class ApproachStop(Approach):
    """Handling approaching stop sign."""

    NAME = "intersection-approach-stop"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.INTERSECTION.APPROACH_SPEED,
    )
    APPROACH_DISTANCE = CONSTANTS.INTERSECTION.APPROACH_DISTANCE_BLIND

    def __init__(self, debug: bool = False):
        """Initialize the ApproachStop."""
        super().__init__(StopState.NAME, debug)


class ApproachGiveWay(Approach):
    """Handling approaching give way sign."""

    NAME = "intersection-approach-give-way"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.INTERSECTION.APPROACH_SPEED,
    )
    APPROACH_DISTANCE = CONSTANTS.INTERSECTION.APPROACH_DISTANCE_BLIND

    def __init__(self, debug: bool = False):
        """Initialize the ApproachGiveWay."""
        super().__init__(GiveWayState.NAME, debug)


class ApproachStopCrossing(BaseState):
    """Handling approaching stop sign."""

    NAME = "intersection-approach-stop-crossing"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.INTERSECTION.APPROACH_SPEED,
    )
    APPROACH_DISTANCE = CONSTANTS.INTERSECTION.APPROACH_DISTANCE

    def __init__(self, debug: bool = False):
        """Initialize the ApproachStop."""
        self.TRANSITIONS = {
            "next": StopState.NAME,
        }
        super().__init__(debug)

    def local_execute(self):
        """Execute the state."""
        super().local_execute()
        start_time = time.perf_counter()

        while self._check_crossing_result():
            if (
                time.perf_counter() - start_time
                > CONSTANTS.INTERSECTION.APPROACH_TIMEOUT
            ):
                self.log_state("ApproachStop: Timeout reached, proceeding to stop")
                return "next"
            time.sleep(0.0001)
            self.log_state("ApproachStop: Approaching stop sign")
        return "next"

    def _check_crossing_result(self):
        """
        Check if the crossing result is valid.

        Returns:
            bool -- True if the crossing line is None or the distance
            to it is less than the approach distance, False otherwise
        """
        crossing_lines = self.blackboard.crossing_lines
        if not crossing_lines or len(crossing_lines) == 0:
            self.log_state("ApproachStop: No crossing lines detected")
            return True

        for line in crossing_lines:
            if line["type"] == CrossingLineType.EGO_SOLID:
                distance = get_distance_to_line(line["start"], line["end"])
                self.log_state(
                    f"ApproachStop: Detected stop sign crossing line at distance {distance:.2f}mm"
                )
                if distance < self.APPROACH_DISTANCE:
                    return True
        return False


class ApproachGiveWayCrossing(BaseState):
    """Handling approaching give way sign."""

    NAME = "intersection-approach-give-way-crossing"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=CONSTANTS.INTERSECTION.APPROACH_SPEED,
    )
    APPROACH_DISTANCE = CONSTANTS.INTERSECTION.APPROACH_DISTANCE

    def __init__(self, debug: bool = False):
        """Initialize the ApproachGiveWay."""
        self.TRANSITIONS = {
            "next": GiveWayState.NAME,
        }
        super().__init__(debug)

    def local_execute(self):
        """Execute the state."""
        super().local_execute()
        start_time = time.perf_counter()

        while self._check_crossing_result():
            if (
                time.perf_counter() - start_time
                > CONSTANTS.INTERSECTION.APPROACH_TIMEOUT
            ):
                self.log_state(
                    "ApproachGiveWay: Timeout reached, proceeding to give way"
                )
                return "next"
            time.sleep(0.0001)
            self.log_state("ApproachGiveWay: Approaching give way sign")
        return "next"

    def _check_crossing_result(self):
        """
        Check if the crossing result is valid.

        Returns:
            bool -- True if the crossing line is None or the distance
            to it is less than the approach distance, False otherwise
        """
        crossing_lines = self.blackboard.crossing_lines
        if not crossing_lines or len(crossing_lines) == 0:
            self.log_state("ApproachGiveWay: No crossing lines detected")
            return True

        for line in crossing_lines:
            if line["type"] in [
                CrossingLineType.EGO_SOLID,
                CrossingLineType.EGO_DOTTED,
            ]:
                distance = get_distance_to_line(line["start"], line["end"])
                self.log_state(
                    f"ApproachGiveWay: Detected give way sign crossing line at distance {distance:.2f}mm"
                )
                if distance < self.APPROACH_DISTANCE:
                    return True
        return False
