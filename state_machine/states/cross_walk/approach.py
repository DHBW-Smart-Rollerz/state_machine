from smarty_utils.enums import Light

from state_machine.components.approach import Approach
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.cross_walk.detect_pedestrian import DetectPedestrian


class ApproachCrosswalk(Approach):
    """Handling approaching the crosswalk."""

    NAME = "crosswalk-approach"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE, max_speed=CONSTANTS.CROSS_WALK.APPROACH_SPEED
    )
    APPROACH_DISTANCE = CONSTANTS.CROSS_WALK.APPROACH_DISTANCE

    def __init__(self, debug: bool = False):
        """Initialize the ApproachStop."""
        super().__init__(DetectPedestrian.NAME, debug)
