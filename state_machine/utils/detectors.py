import numpy as np
from smarty_utils.enums import OBJECTS, SIGNS, Location

from state_machine.utils import RULE_CONSTANTS


def check_dist_to_obj_sign(
    objects: list,
    obj_types: OBJECTS | list[OBJECTS],
    dist_threshold: float,
    location: Location = Location.NOT_RELEVANT,
) -> bool:
    """
    Check if there is an object of a specific type within a certain distance.

    Arguments:
        objects -- list of detected objects or signs
        obj_types -- type of object or list of types to check
        dist_threshold -- distance threshold in meters

    Returns:
        bool -- True if the object is within the distance threshold, False otherwise
    """
    if isinstance(obj_types, OBJECTS) or isinstance(obj_types, SIGNS):
        obj_types = [obj_types]
    # TODO: Check logic with API
    # Add location
    for obj in objects:
        if obj["name"] in obj_types and obj["distance"] < dist_threshold:
            if location == Location.NOT_RELEVANT:
                return True
            elif obj["location"] == location:
                return True
    return False


def dist_to_obj_sign(
    objects: list,
    obj_types: OBJECTS | list[OBJECTS],
    location: Location = Location.NOT_RELEVANT,
) -> float:
    """
    Get the distance to the closest object of a specific type.

    Arguments:
        objects -- list of detected objects or signs
        obj_types -- type of object or list of types to check

    Returns:
        float -- distance to the closest object of the specified type
    """
    if isinstance(obj_types, OBJECTS) or isinstance(obj_types, SIGNS):
        obj_types = [obj_types]
    closest_dist = np.inf
    for obj in objects:
        if obj["name"] in obj_types:
            if obj["distance"] < closest_dist:
                if location == Location.NOT_RELEVANT or obj["location"] == location:
                    closest_dist = obj["distance"]
    return closest_dist


def get_boarders(
    left_lane: any, right_lane: any, x: float = 0.0
) -> tuple[float, float, float]:
    """
    Get the left and right lane boarders.

    Arguments:
        left_lane -- tuple with left lane information (parabola coefficients)
        right_lane -- tuple with right lane information (parabola coefficients)
        x -- x coordinate to evaluate the lane equations

    Returns:
        tuple -- left and right lane boarders
    """
    if left_lane is None or right_lane is None:
        return 0.0, 0.0, 0.0

    left = left_lane(x)
    right = right_lane(x)

    left_boarder = left + 0.5 * RULE_CONSTANTS.lane_width
    right_boarder = right - 0.5 * RULE_CONSTANTS.lane_width
    center_boarder = (left + right) / 2

    return left_boarder, center_boarder, right_boarder


def _get_position(
    left_boarder: float,
    center_boarder: float,
    right_boarder: float,
    ly: float = 0.0,
    ry: float = 0.0,
) -> Location:
    """
    Get the position of the car based on the lane boarders.

    Arguments:
        left_boarder -- left lane boarder
        center_boarder -- center lane boarder
        right_boarder -- right lane boarder

    Returns:
        Location -- location of the obj
    """
    # 1. Case is in the right lane
    if left_boarder > ly and right_boarder < ry:
        if center_boarder < (ly + ry) / 2:
            return Location.LEFT_LANE
        else:
            return Location.RIGHT_LANE
    elif left_boarder < ly:
        return Location.LEFT
    # 4. Case is right of the right lane
    elif right_boarder > ry:
        return Location.RIGHT
    # 5. We don't know where the is
    return Location.UNKNOWN


def get_car_location(left_lane: any, right_lane: any) -> Location:
    """
    Get the location of the car based on the lane information.
    Car center is fixed at (0,0).

    Arguments:
        left_lane -- tuple with left lane information (parabola coefficients)
        right_lane -- tuple with right lane information (parabola coefficients)

    Returns:
        Location -- location of the car
    """
    if left_lane is None or right_lane is None:
        return Location.UNKNOWN

    left_boarder, center_boarder, right_boarder = get_boarders(
        left_lane, right_lane, 0.0
    )

    return _get_position(left_boarder, center_boarder, right_boarder)


def get_object_location(obj_position: dict, left_line: any, right_line: any) -> tuple:
    """Get the location of the object."""
    assert isinstance(obj_position, dict), "Invalid object position type"
    lx = obj_position["bottom_left_x"]
    rx = obj_position["bottom_right_x"]
    ly = obj_position["bottom_left_y"]
    ry = obj_position["bottom_right_y"]

    if left_line is None or right_line is None:
        return Location.UNKNOWN

    left_boarder, center_boarder1, _ = get_boarders(left_line, right_line, lx)
    _, center_boarder2, right_boarder = get_boarders(left_line, right_line, rx)
    center_boarder = np.mean([center_boarder1, center_boarder2])

    return _get_position(left_boarder, center_boarder, right_boarder, ly, ry)
