import threading
import time

import numpy as np
import yasmin
from smarty_utils.enums import (
    OBJECTS,
    SIGNS,
    Light,
    Location,
    Nodes,
    NodeState,
    StateMachineTestModes,
)

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


class BlackBoard:
    """Describes the state including maximal speed, lane, and other parameters."""

    instance = None

    def __new__(cls, *args, **kwargs):
        """Generate a singleton instance of the blackboard."""
        if cls.instance is None:
            cls.instance = super(BlackBoard, cls).__new__(cls)
        return cls.instance

    def __init__(
        self,
        light_configuration: TopicStateParameter = None,
        max_speed: TopicStateParameter = None,
        goal_lane: TopicStateParameter = None,
        car_lane: TopicStateParameter = None,
        objects: StateParameter = None,
        signs: StateParameter = None,
        lane_coefficients: StateParameter = None,
        last_state: TopicStateParameter = None,
        last_timestamp: StateParameter = None,
        node_states: dict[Nodes, ParameterStateParameter] = {},
        remote_state: StateParameter = None,
        test_mode: int = 0,
        use_crossing_detection: bool = True,
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
        if hasattr(self, "_initialized") and self._initialized:
            return
        if any(
            param is None
            for param in [
                light_configuration,
                max_speed,
                goal_lane,
                car_lane,
                objects,
                signs,
                lane_coefficients,
                last_state,
                last_timestamp,
                remote_state,
            ]
        ):
            raise ValueError(
                "All parameters must be provided for BlackBoard initialization"
            )
        self._initialized = True
        self.__lock = threading.Lock()
        self._initial_state = [
            light_configuration.value,
            max_speed.value,
            goal_lane.value,
            car_lane.value,
            objects.value,
            signs.value,
            lane_coefficients.value,
            last_state.value,
            last_timestamp.value,
            remote_state.value,
            {key: p.value for key, p in node_states.items()},
        ]
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
        self._start_location = Location.UNKNOWN
        self._other_parameters = {}
        self._test_mode = test_mode
        self._crossing_lines = []
        self._use_crossing_detection = use_crossing_detection

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

    def reset(self):
        """Reset the blackboard to default values."""
        with self.__lock:
            for param, value in zip(
                [
                    self._light_configuration,
                    self._max_speed,
                    self._goal_lane,
                    self._car_lane,
                    self._objects,
                    self._signs,
                    self._lane_coefficients,
                    self._last_state,
                    self._last_timestamp,
                    self._remote_state,
                    self._node_states,
                ],
                self._initial_state,
            ):
                if isinstance(param, dict):
                    # value is {Nodes: initial_int_value}
                    for key, initial_value in value.items():
                        if key in param:
                            param[key].value = initial_value
                else:
                    param.value = value
            self._current_state = "No State"
            self._speed_limit = np.inf
            self._has_speed_limit = False
            self._free_drive = False
            self._other_parameters = {}

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

    @current_state.setter
    def current_state(self, state: str):
        """Set the current state."""
        with self.__lock:
            self._current_state = state

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

    @property
    def test_mode(self) -> int:
        """Get the test mode."""
        with self.__lock:
            return self._test_mode

    @property
    def has_speed_limit(self) -> bool:
        """Check if a speed limit is currently active."""
        with self.__lock:
            return self._has_speed_limit

    @property
    def start_location(self) -> Location:
        """Get the start location."""
        with self.__lock:
            return self._start_location

    @start_location.setter
    def start_location(self, location: Location):
        """Set the start location."""
        with self.__lock:
            self._start_location = location

    @property
    def crossing_lines(self) -> list[dict]:
        """Get the distance to crossing."""
        with self.__lock:
            return self._crossing_lines

    @crossing_lines.setter
    def crossing_lines(self, lines: list[dict]):
        """Set the distance to crossing."""
        with self.__lock:
            self._crossing_lines = lines

    @property
    def use_crossing_detection(self) -> bool:
        """Check if crossing detection should be used."""
        with self.__lock:
            return self._use_crossing_detection

    def __getattr__(self, name: str):
        """Get unknown attributes from other_parameters dict."""
        # Prevent infinite recursion during early initialization
        # __getattr__ is only called when normal lookup fails, so private
        # attributes that are missing should raise immediately.
        if name.startswith("_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        # Check if it's a property on the class — if so, the fact that we
        # reached __getattr__ means the underlying private attribute doesn't
        # exist yet (early init). Raise AttributeError to signal that.
        for cls in type(self).__mro__:
            if name in cls.__dict__ and isinstance(cls.__dict__[name], property):
                raise AttributeError(
                    f"'{type(self).__name__}' property '{name}' is not yet initialized"
                )

        # Guard against access before __lock is initialized
        try:
            lock = object.__getattribute__(self, "_BlackBoard__lock")
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        # Look up in _other_parameters with thread safety
        with lock:
            try:
                other_params = object.__getattribute__(self, "_other_parameters")
                if name in other_params:
                    return other_params[name]
            except AttributeError:
                pass

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name: str, value):
        """Set unknown attributes in other_parameters dict."""
        # Allow private attributes to be set directly
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        # Check if the attribute is a property (descriptor) on the class
        for cls in type(self).__mro__:
            if name in cls.__dict__:
                attr = cls.__dict__[name]
                if isinstance(attr, property):
                    # Invoke the property setter
                    attr.fset(self, value)
                    return
                else:
                    # It's a regular class attribute, set it directly
                    object.__setattr__(self, name, value)
                    return

        # Check if it's already in the instance dict
        if name in self.__dict__:
            object.__setattr__(self, name, value)
            return

        # Otherwise, store in _other_parameters
        with self.__lock:
            self._other_parameters[name] = value

    def __str__(self):
        """
        String representation of the blackboard.

        Returns:
            str -- String representation of the blackboard
        """
        return f"Blackboard(signs={self._signs}, objects={self._objects}, light_configuration={self._light_configuration}, max_speed={self._max_speed}, goal_lane={self._goal_lane}, car_lane={self._car_lane}, lane_coefficients={self._lane_coefficients}, last_state={self._last_state}, last_timestamp={self._last_timestamp}, node_states={{key: param.value for key, param in self._node_states.items()}}, remote_state={self._remote_state}, current_state={self._current_state})"
