class START_BOX_CONSTANTS:
    """CONSTANTS for the startbox state machine."""

    # Time to wait before considering the start box detected
    READY_TIME_THRESH = 3.0  # seconds

    # Time to wait before forgetting the start box detection
    FORGET_READY_TIME_THRESH = 3.0  # seconds

    # Time to wait before considering the search as timed out
    SEARCH_TIMEOUT = 60.0 * 5  # seconds (5 minutes)

    # Time to wait before considering the start box as OPEN
    READY_TIMEOUT = 60.0 * 5  # seconds

    # Distance threshold for the start box detection
    DISTANCE_THRESH = 500  # millimeters
