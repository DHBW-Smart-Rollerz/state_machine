class INTERSECTION_CONSTANTS:
    """CONSTANTS for the intersection state machine."""

    # The distance to the object in front of the car when intersecting
    START_DIST = 300  # mm
    GIVE_WAY_DIST = 300  # mm

    # The time in seconds until the ready state is canceled
    READY_TIMEOUT = 10

    # The time in seconds until the intersecting is canceled
    TIMEOUT = 15  # s TODO: CHECK THIS VALUE
    WAIT_TIMEOUT = 10  # s

    # The distance to the object in front of the car when intersecting
    VEHICLE_DIST = 650  # mm TODO: CHECK THIS VALUE

    # The minimal time to check for cars
    STOP_NO_CAR_TIMEOUT = 3  # s
    GIVE_NO_CAR_TIMEOUT = 1  # s

    # Maximum speed in m/s
    MAX_SPEED = 0.1  # m/s
    APPROACH_SPEED = 0.1  # m/s
    APPROACH_DISTANCE_BLIND = 800  # mm
    APPROACH_DISTANCE = 800  # mm
    APPROACH_TIMEOUT = 2.3  # s # Fallback for crossing detection
