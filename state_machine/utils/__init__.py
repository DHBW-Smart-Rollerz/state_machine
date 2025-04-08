import enum


class Location(enum.Enum):
    """Location of the object."""

    LEFT = "left"
    RIGHT = "right"
    FRONT = "front"
    BACK = "back"
    UNKNOWN = "unknown"
    NOT_RELEVANT = "not_relevant"
