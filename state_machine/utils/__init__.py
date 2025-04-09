import enum


class Location(enum.Enum):
    """Location of the object."""

    LEFT = "left"
    RIGHT = "right"
    FRONT = "front"
    BACK = "back"
    UNKNOWN = "unknown"
    NOT_RELEVANT = "not_relevant"

    @staticmethod
    def opposite(location: "Location") -> "Location":
        """
        Get the opposite location of a given location.

        Arguments:
            location -- Location to get the opposite of

        Returns:
            Location -- Opposite location
        """
        if location == Location.LEFT:
            return Location.RIGHT
        elif location == Location.RIGHT:
            return Location.LEFT
        elif location == Location.FRONT:
            return Location.BACK
        elif location == Location.BACK:
            return Location.FRONT
        else:
            return location
