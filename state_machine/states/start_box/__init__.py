from state_machine.states.start_box.ready import ReadyState
from state_machine.states.start_box.search import SearchState

__all__ = [
    "ReadyState",
    "SearchState",
]


def detect(signs: list[dict], dist_thresh: float) -> bool:
    """
    Detect the start box.

    Arguments:
        signs -- List of signs
        dist_thresh -- Distance threshold to consider the start box detected

    Returns:
        bool -- True if the start box is detected, False otherwise
    """
    for sign in signs:
        if sign.get("name") == "stop_sign":
            d = sign.get("distance")
            if d and d < dist_thresh:
                return True

    return False


class START_BOX_CONSTANTS:
    """CONSTANTS for the startbox state machine."""

    # Time to wait before considering the start box detected
    READY_TIME_THRESH = 3.0  # seconds

    # Time to wait before forgetting the start box detection
    FORGET_READY_TIME_THRESH = 1.0  # seconds

    # Time to wait before considering the search as timed out
    SEARCH_TIMEOUT = 60.0 * 5  # seconds (5 minutes)

    # Time to wait before considering the start box as OPEN
    READY_TIMEOUT = 60.0  # seconds

    # Distance threshold for the start box detection
    DISTANCE_THRESH = 0.5  # meters
