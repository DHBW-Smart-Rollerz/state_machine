import time

from smarty_utils.enums import OBJECTS, Light, Location

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.utils.detectors import check_dist_to_obj_sign


class WaitState(BaseState):
    """Handling waiting on pedestrian to cross Crosswalk."""

    NAME = "crosswalk-wait"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE_NORMAL,
        max_speed=0.0,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "done": "done",
        }
        super().__init__(debug)

    def local_execute(self, blackboard: BlackBoard):
        """Execute the state."""
        super().local_execute(blackboard)

        start_location = Location.UNKNOWN
        while start_location == Location.UNKNOWN:
            start_location = self.get_start_location()
            time.sleep(0.0001)
            self.log_state("Crosswalk: Waiting for pedestrian to be detected")
        time.sleep(2)
        self.log_state(
            f"Crosswalk: Pedestrian detected at {start_location}; {self.check_crossed(start_location)}; {Location.opposite(start_location)}"
        )
        while not self.check_crossed(start_location):
            time.sleep(0.0001)
            self.log_state("Crosswalk: Waiting for pedestrian to cross Crosswalk")

        return "done"

    def check_crossed(self, start_location: Location):
        """
        Check if the pedestrian has crossed the Crosswalk.

        The pedestrian is considered to have crossed when they:
          - appear at the opposite side of the road (out-of-lane), OR
          - appear in the opposite lane (in-lane opposite), OR
          - are no longer visible within the crosswalk distance

        Arguments:
            start_location -- The starting location of the pedestrian

        Returns:
            bool -- True if the pedestrian has crossed the Crosswalk, False otherwise
        """
        # Opposite outside-road zone (e.g. LEFT → RIGHT, RIGHT_LANE → LEFT)
        opposite_out = Location.opposite(start_location, True)
        # Opposite lane zone (e.g. LEFT → RIGHT, LEFT_LANE → RIGHT_LANE)
        opposite_in = Location.opposite(start_location, False)

        reached_opposite = check_dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
            CONSTANTS.CROSS_WALK.PEDESTRIAN_DIST,
            opposite_out,
        ) or check_dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
            CONSTANTS.CROSS_WALK.PEDESTRIAN_DIST,
            opposite_in,
        )

        disappeared = not check_dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
            CONSTANTS.CROSS_WALK.PEDESTRIAN_DIST,
            Location.NOT_RELEVANT,
        )

        return reached_opposite or disappeared

    def get_start_location(self):
        """
        Get the starting location of the pedestrian.

        Returns:
            Location -- The starting location of the pedestrian
        """
        for obj in self.blackboard.objects:
            if (
                obj["name"] in [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN]
                and obj["distance"] < CONSTANTS.CROSS_WALK.PEDESTRIAN_DIST
            ):
                return obj["location"]
        return Location.UNKNOWN
