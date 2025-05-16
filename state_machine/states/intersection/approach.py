from smarty_utils.enums import Light

from state_machine.components.approach import Approach
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.intersection.give_way import GiveWayState
from state_machine.states.intersection.stop import StopState


class ApproachStop(Approach):
    """Handling approaching stop sign."""

    NAME = "intersection-approach-stop"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE_NORMAL,
        max_speed=CONSTANTS.INTERSECTION.APPROACH_SPEED,
    )
    APPROACH_DISTANCE = CONSTANTS.INTERSECTION.APPROACH_DISTANCE

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
    APPROACH_DISTANCE = CONSTANTS.INTERSECTION.APPROACH_DISTANCE

    def __init__(self, debug: bool = False):
        """Initialize the ApproachGiveWay."""
        super().__init__(GiveWayState.NAME, debug)
