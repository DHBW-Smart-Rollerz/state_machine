class INTERSECTION_CONSTANTS:
    """CONSTANTS for the intersection state machine."""

    # The distance to the object in front of the car when intersecting
    START_DIST = 300  # mm
    GIVE_WAY_DIST = 300  # mm

    # The time in seconds until the ready state is canceled
    READY_TIMEOUT = 10

    # The time in seconds until the intersecting is canceled
    TIMEOUT = 30  # s
    WAIT_TIMEOUT = 10  # s

    # The distance to the object in front of the car when intersecting
    VEHICLE_DIST = 1500  # mm

    # The minimal time to check for cars
    STOP_NO_CAR_TIMEOUT = 3  # s
    GIVE_NO_CAR_TIMEOUT = 1  # s

    # Maximum speed in m/s
    MAX_SPEED = 0.1  # m/s
    APPROACH_SPEED = 0.1  # m/s
    APPROACH_DISTANCE_BLIND = 300  # mm
    APPROACH_DISTANCE = 120  # mm
    APPROACH_TIMEOUT = 5  # s # Fallback for crossing detection
