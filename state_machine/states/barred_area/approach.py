from smarty_utils.enums import Light

from state_machine.components.approach import Approach
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.barred_area.detect_obstacle import DetectObstacleState


class ApproachBarredArea(Approach):
    """Handling approaching Barred area."""

    NAME = "barred-area-approach"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BLINK_LEFT_NORMAL,
        max_speed=CONSTANTS.BARRED_AREA.APPROACH_SPEED,
    )
    APPROACH_DISTANCE = CONSTANTS.BARRED_AREA.APPROACH_DISTANCE

    def __init__(self, debug: bool = False):
        """Initialize the ApproachStop."""
        super().__init__(DetectObstacleState.NAME, debug)
