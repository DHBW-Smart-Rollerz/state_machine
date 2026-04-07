import time

import numpy as np
from smarty_utils.enums import OBJECTS, Light, Location

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states import CONSTANTS
from state_machine.states.barred_area.switch_lane import SwitchLaneState
from state_machine.utils.detectors import dist_to_obj_sign


class WaitState(BaseState):
    """Handling waiting vehicles on Barred Area."""

    NAME = "barred-area-wait"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.BRAKE_NORMAL,
        max_speed=0.0,
    )

    def __init__(self, debug: bool = False):
        """Initialize the Wait State."""
        self.TRANSITIONS = {
            "switch": SwitchLaneState.NAME,
        }
        super().__init__(debug)
        self._last_closest_dist = np.inf

    def local_execute(self):
        """Execute the state."""
        super().local_execute()

        while self._last_closest_dist == np.inf:
            self._last_closest_dist = dist_to_obj_sign(
                self.blackboard.objects,
                [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
                location=Location.LEFT_LANE,
            )
            time.sleep(0.0001)
            self.log_state("Barred Area: Waiting for vehicle to be detected")
        time.sleep(2)
        self.log_state(
            f"Barred Area: Pedestrian detected at {self._last_closest_dist} mm;"
        )
        start_time = time.perf_counter()
        while (
            self.check_crossed()
            and time.perf_counter() - start_time < CONSTANTS.BARRED_AREA.WAIT_TIMEOUT
        ):
            time.sleep(0.0001)
            self.update()
            self.log_state("Barred Area: Waiting for vehicle to cross Barred Area")

        return "switch"

    def update(self):
        """Update the state with the latest information."""
        d_left = dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
            location=Location.LEFT_LANE,
        )
        d_unknown = dist_to_obj_sign(
            self.blackboard.objects,
            [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
            location=Location.UNKNOWN,
        )
        self._last_closest_dist = min(d_left, d_unknown)

    def check_crossed(self):
        """
        Check if the vehicle has crossed the Barred Area.

        Returns:
            bool -- True if the vehicle has crossed the Barred Area, False otherwise
        """
        self._time_since_clear = getattr(self, "_time_since_clear", None)
        current_time = time.perf_counter()

        if self._last_closest_dist > CONSTANTS.BARRED_AREA.OBSTACLE_DIST:
            if self._time_since_clear is None:
                self._time_since_clear = current_time
            return (
                current_time - self._time_since_clear < CONSTANTS.BARRED_AREA.WAIT_DELAY
            )
        else:
            self._time_since_clear = None
            return True
