import time

import yasmin
from smarty_utils.enums import OBJECTS, Light, Location

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import StateDescription
from state_machine.states import CONSTANTS
from state_machine.utils.detectors import check_dist_to_obj_sign


class WaitState(BaseState):
    """Handling waiting on car to cross intersection."""

    NAME = "intersection-wait"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=0.0,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "done": "done",
        }
        super().__init__(debug)

    def local_execute(self):
        """Execute the state."""
        super().local_execute()

        start_location = Location.UNKNOWN
        while start_location == Location.UNKNOWN and not self._check_timeout():
            start_location = self.get_start_location()
            time.sleep(0.0001)
            self.log_state("Intersection: Waiting for vehicle to be detected")
        # time.sleep(2)
        self.log_state(
            f"Intersection: Vehicle detected at {start_location}; {self.check_crossed(start_location)}; {Location.opposite(start_location)}"
        )
        while not self.check_crossed(start_location) and not self._check_timeout():
            time.sleep(0.0001)
            self.log_state("Intersection: Waiting for vehicle to cross intersection")

        return "done"

    def _check_timeout(self):
        """
        Check if the timeout has been reached.

        Returns:
            bool -- True if the timeout has been reached, False otherwise
        """
        self.log_state(
            f"Intersection: Time elapsed {time.perf_counter() - self.blackboard.last_timestamp:.2f}s"
        )
        return (
            time.perf_counter() - self.blackboard.last_timestamp
            > CONSTANTS.INTERSECTION.TIMEOUT
        )

    def check_crossed(self, start_location: Location):
        """
        Check if the car has crossed the intersection.

        Arguments:
            start_location -- The starting location of the car

        Returns:
            bool -- True if the car has crossed the intersection, False otherwise
        """
        return check_dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
            CONSTANTS.INTERSECTION.VEHICLE_DIST,
            Location.opposite(start_location),
        ) or check_dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
            CONSTANTS.INTERSECTION.VEHICLE_DIST,
            Location.UNKNOWN,
        )

    def get_start_location(self):
        """
        Get the starting location of the car.

        Returns:
            Location -- The starting location of the car
        """
        for obj in self.blackboard.objects:
            if (
                obj["name"] in [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN]
                and obj["distance"] < CONSTANTS.INTERSECTION.VEHICLE_DIST
            ):
                return obj["location"]
        return Location.UNKNOWN
