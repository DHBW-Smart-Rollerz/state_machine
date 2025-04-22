import time

import yasmin
from smarty_utils.enums import OBJECTS, Light

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.utils import Location
from state_machine.utils.detectors import check_dist_to_obj_sign


class WaitState(BaseState):
    """Handling waiting on car to cross intersection."""

    NAME = "wait_intersection"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE,
        max_speed=0,
    )

    def __init__(self, debug: bool = False):
        """Initialize the ReadyState."""
        self.TRANSITIONS = {
            "done": "done",
        }
        super().__init__(debug)

    def execute(self, blackboard: BlackBoard):
        """
        Execute the state.

        Arguments:
            blackboard -- The blackboard containing the state information

        Returns:
            str -- The next state to transition to
        """
        super().execute(blackboard)

        start_time = time.perf_counter()
        start_location = Location.UNKNOWN
        while start_location == Location.UNKNOWN:
            start_location = self.get_start_location()
            time.sleep(0.0001)
            if (
                time.perf_counter() - start_time
            ) % CONSTANTS.INTERSECTION.LOG_TIME == 0:
                yasmin.YASMIN_LOG_INFO(
                    "Intersection - WAIT: Waiting for vehicle to be detected"
                )

        while self.check_crossed(start_location):
            time.sleep(0.0001)
            if (
                time.perf_counter() - start_time
            ) % CONSTANTS.INTERSECTION.LOG_TIME == 0:
                yasmin.YASMIN_LOG_INFO(
                    "Intersection - WAIT: Waiting for vehicle to cross intersection"
                )

        return "done"

    def check_crossed(self, start_location: Location):
        """
        Check if the car has crossed the intersection.

        Arguments:
            start_location -- The starting location of the car

        Returns:
            bool -- True if the car has crossed the intersection, False otherwise
        """
        return not check_dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE],
            CONSTANTS.INTERSECTION.VEHICLE_DIST,
            start_location,  # TODO: Think about this logic
        )

    def get_start_location(self):
        """
        Get the starting location of the car.

        Returns:
            Location -- The starting location of the car
        """
        for obj in self.blackboard.objects:
            if (
                obj["name"] == OBJECTS.VEHICLE
                and obj["distance"] < CONSTANTS.INTERSECTION.VEHICLE_DIST
            ):
                return obj["location"]
        return Location.UNKNOWN
