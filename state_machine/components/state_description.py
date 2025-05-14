import threading
import time

import numpy as np
import yasmin
from smarty_utils.enums import OBJECTS, SIGNS, Light, Location, Nodes, NodeState

from state_machine.components.state_parameter import (
    ParameterStateParameter,
    StateParameter,
    TopicStateParameter,
)


class StateDescription:
    """Describes properties of a state."""

    def __init__(
        self,
        light_configuration: Light = None,
        max_speed: float = None,
        goal_lane: Location = None,
        node_states: dict[Nodes, NodeState] = None,
    ):
        """
        Initialize the state description.

        Keyword Arguments:
            light_configuration -- Light configuration
            max_speed -- Maximum speed
            goal_lane -- Goal lane
            node_states -- Node states
        """
        self.light_configuration = light_configuration
        self.max_speed = max_speed
        self.goal_lane = goal_lane
        self.node_states = node_states


class BlackBoard(yasmin.Blackboard):
    """Describes the state including maximal speed, lane, and other parameters."""

    def __init__(
        self,
        light_configuration: TopicStateParameter,
        max_speed: TopicStateParameter,
        goal_lane: TopicStateParameter,
        car_lane: TopicStateParameter,
        objects: StateParameter,
        signs: StateParameter,
        lane_coefficients: StateParameter,
        last_state: TopicStateParameter,
        last_timestamp: StateParameter,
        node_states: dict[Nodes, ParameterStateParameter],
        remote_state: StateParameter,
    ):
        """
        Initialize the state description.

        Keyword Arguments:
            light_configuration -- Light configuration
            max_speed -- Maximum speed
            goal_lane -- Goal lane
            car_lane -- Car lane
            objects -- Objects detected
            signs -- Signs detected
            lane_coefficients -- Lane coefficients
            last_state -- Last state
            last_timestamp -- Last timestamp
            node_states -- Node states
            remote_state -- Remote state
        """
        super().__init__()
        self.__lock = threading.Lock()
        self._light_configuration = light_configuration
        self._max_speed = max_speed
        self._goal_lane = goal_lane
        self._car_lane = car_lane
        self._objects = objects
        self._signs = signs
        self._lane_coefficients = lane_coefficients
        self._last_state = last_state
        self._last_timestamp = last_timestamp
        self._node_states = node_states
        self._remote_state = remote_state
        self._current_state = "No State"
        self._speed_limit = np.inf
        self._has_speed_limit = False
        self._free_drive = False

    def update(self, state_description: StateDescription):
        """
        Update the state description.

        Arguments:
            state_description -- State description
        """
        if state_description.light_configuration is not None:
            self.light_configuration = state_description.light_configuration
        if state_description.max_speed is not None:
            self.max_speed = state_description.max_speed
        if state_description.goal_lane is not None:
            self.goal_lane = state_description.goal_lane
        if state_description.node_states is not None:
            for key, state in state_description.node_states.items():
                assert key in self._node_states.keys(), f"Key {key} not in node states"
                self._node_states[key].value = state.value

    def reset_speed_limit(self):
        """Reset the speed limit."""
        with self.__lock:
            self._has_speed_limit = False
            self._speed_limit = np.inf

    @property
    def light_configuration(self) -> Light:
        """Get the light configuration."""
        with self.__lock:
            return self._light_configuration.value

    @light_configuration.setter
    def light_configuration(self, light: Light):
        """Set the light configuration."""
        with self.__lock:
            self._light_configuration.value = light

    @property
    def max_speed(self) -> float:
        """Get the maximum speed."""
        with self.__lock:
            return min(self._max_speed.value, self._speed_limit)

    @property
    def speed_limit(self) -> float:
        """Get the speed limit."""
        with self.__lock:
            return self._speed_limit

    @speed_limit.setter
    def speed_limit(self, speed: float):
        """Set the speed limit."""
        with self.__lock:
            self._has_speed_limit = True
            self._speed_limit = speed

    @max_speed.setter
    def max_speed(self, speed: float):
        """Set the maximum speed."""
        with self.__lock:
            self._max_speed.value = speed

    @property
    def free_drive(self) -> bool:
        """Get the free drive status."""
        with self.__lock:
            return self._free_drive

    @free_drive.setter
    def free_drive(self, free: bool):
        """Set the free drive status."""
        with self.__lock:
            self._free_drive = free
            if free:
                self._speed_limit = np.inf
                self._has_speed_limit = False

    @property
    def goal_lane(self) -> Location:
        """Get the goal lane."""
        with self.__lock:
            return self._goal_lane.value

    @goal_lane.setter
    def goal_lane(self, lane: Location):
        """Set the goal lane."""
        with self.__lock:
            self._goal_lane.value = lane

    @property
    def car_lane(self) -> Location:
        """Get the car lane."""
        with self.__lock:
            return self._car_lane.value

    @car_lane.setter
    def car_lane(self, lane: Location):
        """Set the car lane."""
        with self.__lock:
            self._car_lane.value = lane

    @property
    def objects(self) -> list[OBJECTS]:
        """Get the detected objects."""
        with self.__lock:
            return self._objects.value

    @objects.setter
    def objects(self, detected_objects: list[dict]):
        """Set the detected objects."""
        with self.__lock:
            self._objects.value = detected_objects

    @property
    def signs(self) -> list[SIGNS]:
        """Get the detected signs."""
        with self.__lock:
            return self._signs.value

    @signs.setter
    def signs(self, detected_signs: list[dict]):
        """Set the detected signs."""
        with self.__lock:
            self._signs.value = detected_signs

    @property
    def lane_coefficients(self) -> dict[str, tuple]:
        """Get the lane coefficients."""
        with self.__lock:
            return self._lane_coefficients.value

    @lane_coefficients.setter
    def lane_coefficients(self, coefficients: dict[str, tuple]):
        """Set the lane coefficients."""
        with self.__lock:
            self._lane_coefficients.value = coefficients

    @property
    def last_state(self) -> str:
        """Get the last state."""
        with self.__lock:
            return self._last_state.value

    @last_state.setter
    def last_state(self, state: str):
        """Set the last state."""
        with self.__lock:
            if state == self._last_state.value:
                return
            self._last_state.value = state
            self._last_timestamp.value = time.perf_counter()

    @property
    def last_timestamp(self) -> float:
        """Get the last timestamp."""
        with self.__lock:
            return self._last_timestamp.value

    @last_timestamp.setter
    def last_timestamp(self, timestamp: float):
        """Set the last timestamp."""
        with self.__lock:
            self._last_timestamp.value = timestamp

    @property
    def current_state(self) -> str:
        """Get the current state."""
        with self.__lock:
            return self._current_state

    @property
    def node_states(self) -> dict[str, NodeState]:
        """Get the node states."""
        with self.__lock:
            return {key: param.value for key, param in self._node_states.items()}

    @node_states.setter
    def node_states(self, states: dict[str, NodeState]):
        """Set the node states."""
        with self.__lock:
            for key, state in states.items():
                self._node_states[key].value = state.value

    @property
    def remote_state(self) -> int:
        """Get the remote state."""
        with self.__lock:
            return self._remote_state.value

    @remote_state.setter
    def remote_state(self, state: int):
        """Set the remote state."""
        with self.__lock:
            self._remote_state.value = state

    def __str__(self):
        """
        String representation of the blackboard.

        Returns:
            str -- String representation of the blackboard
        """
        return f"Blackboard(signs={self._signs})"
