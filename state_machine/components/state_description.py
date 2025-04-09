import enum

import yasmin
from flask.cli import F

from state_machine.utils import Location


class Light(enum.Enum):
    """Enum for light states."""

    BLINK_LEFT = 0b00000001
    BLINK_RIGHT = 0b00000010
    NORMAL = 0b00000000
    BRAKE = 0b00000100
    WARNING = 0b00001000


class OBJECTS(enum.Enum):
    """Enum for object types."""

    VEHICLE = "vehicle"
    PEDESTRIAN = "pedestrian"


class SIGNS(enum.Enum):
    """Enum for sign types."""

    STOP = "stop"
    YIELD = "yield"
    NO_OVERTAKING = "no_overtaking"
    NO_OVERTAKING_LIFTED = "no_overtaking_lifted"
    FAST_TRACK = "fast_track"
    FAST_TRACK_LIFTED = "fast_track_lifted"
    SPEED_LIMIT_30 = "speed_limit_30"
    SPEED_LIMIT_30_LIFTED = "speed_limit_30_lifted"
    CROSSWALK = "crosswalk"
    PRIORITY_ONCOMING_TRAFFIC = "priority_oncoming_traffic"
    PARKING = "parking"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GIVE_WAY = "give_way"
    PRIORITY = "priority"


class Nodes(enum.Enum):
    """Computation Nodes."""

    LANE_DETECTION = "lane_detection"
    OBJECT_DETECTION = "object_detection"
    PATH_PLANNING = "path_planning"
    CONTROL = "control"
    STATE_ESTIMATION = "state_estimation"


class NodesModes(enum.Enum):
    """Enum for node states."""

    ACTIVE = 0
    INACTIVE = 1
    RESET = 2

    @staticmethod
    def get_publisher_name(node: Nodes) -> str:
        """Get the publisher name for the node mode."""
        return f"{node.value}_mode_publisher"

    @staticmethod
    def get_all_publishers() -> list[str]:
        """Get all publisher names for node modes."""
        return [NodesModes.get_publisher_name(node) for node in Nodes]


class StateDescription:
    """Describes the state including maximal speed, lane, and other parameters."""

    def __init__(
        self,
        light_configuration: Light = None,
        max_speed: float = None,
        goal_lane: Location = None,
        node_modes: dict[Nodes, NodesModes] = {},
        publishers: dict[str, callable] = {},
    ):
        """
        Initialize the state description.

        Keyword Arguments:
            light_configuration -- Light Config (default: {None})
            max_speed -- Maximal Speed to set (default: {None})
            goal_lane -- Lane to switch to (default: {None})
            node_modes -- Modes of each node (default: {{}})
            publishers -- Publisher functions for the node modes (default: {{}})
        """
        self.light_configuration = light_configuration
        self.max_speed = max_speed
        self.goal_lane = goal_lane
        self.node_modes: dict[Nodes, NodesModes] = node_modes
        self.publishers = publishers

    @property
    def publishers(self):
        """Get the publishers."""
        return self._publishers

    @publishers.setter
    def publishers(self, publishers: dict[str, callable]):
        """Set the publishers."""
        self._publishers = self._check_publishers(publishers)

    def _check_publishers(self, publishers: dict[str, callable]) -> dict[str, callable]:
        """Check if the publishers are callable and match the required attributes."""
        for key, value in publishers.items():
            if not callable(value):
                raise ValueError(f"Publisher for '{key}' is not callable.")
        return publishers

    def publish_and_set_difference(self, other: "StateDescription"):
        """Publish the difference between two state descriptions."""
        diff = self.difference(other)
        for key, value in diff.items():
            if key in self._publishers:
                if self.publishers[key](value):
                    self.__setattr__(key, value)
                else:
                    yasmin.YASMIN_LOG_WARN(
                        f"Failed to publish '{key}' with value '{value}'."
                    )
            else:
                yasmin.YASMIN_LOG_WARN(f"Publisher for '{key}' not found.")

    def difference(self, other: "StateDescription") -> dict:
        """Calculate the difference between two state descriptions."""
        diff = {}
        if (
            other.light_configuration
            and self.light_configuration != other.light_configuration
        ):
            diff["light_configuration"] = other.light_configuration
        if other.max_speed and self.max_speed != other.max_speed:
            diff["max_speed"] = other.max_speed
        if other.goal_lane and self.goal_lane != other.goal_lane:
            diff["goal_lane"] = other.goal_lane
        for node in other.node_modes.keys():
            if self.node_modes.get(node, None) != other.node_modes[node]:
                diff[node] = other.node_modes[node]
        return diff
