import numpy as np
import state_msgs.msg
import yasmin
from smarty_utils.enums import OBJECTS, SIGNS, Location

from state_machine.utils import RULE_CONSTANTS


def check_dist_to_obj_sign(
    objects: list,
    obj_types: OBJECTS | list[OBJECTS] | SIGNS | list[SIGNS],
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

    x /= 1000  # Convert from mm to m for lane evaluation (assuming lane equations are in meters)
    left = left_lane(x) * 1000  # Convert back to mm for boarder calculations
    right = right_lane(x) * 1000  # Convert back to mm for boarder calculations

    left_boarder = left + 0.5 * RULE_CONSTANTS.lane_width
    right_boarder = right - 0.5 * RULE_CONSTANTS.lane_width
    center_boarder = (left + right) / 2

    return left_boarder, center_boarder, right_boarder


def get_car_location(left_lane: any, right_lane: any) -> Location:
    """
    Get the location of the car based on the lane information.

    The car's reference point is the centre of the front axle, which is fixed
    at the ego-coordinate origin (x=0, y=0).  X points forward, Y points left.

    The Y=0 point is classified against the four road zones evaluated at x=0:
      - LEFT       : y=0 is left  of the left road border  (Y > left_boarder)
      - LEFT_LANE  : y=0 is in the left (oncoming) lane
      - RIGHT_LANE : y=0 is in the right (ego) lane
      - RIGHT      : y=0 is right of the right road border (Y < right_boarder)

    Arguments:
        left_lane  -- callable parabola for the left  lane line (higher Y)
        right_lane -- callable parabola for the right lane line (lower  Y)

    Returns:
        Location -- LEFT, LEFT_LANE, RIGHT_LANE, RIGHT, or UNKNOWN
    """
    if left_lane is None or right_lane is None:
        return Location.UNKNOWN

    # Evaluate lane borders at the front-axle position (x=0)
    left_boarder, center_boarder, right_boarder = get_boarders(
        left_lane, right_lane, 0.0
    )
    # left_boarder >= center_boarder >= right_boarder  (Y axis points left)

    car_y = 0.0  # front-axle centre in ego coordinates

    loc = Location.UNKNOWN
    if car_y >= left_boarder:
        loc = Location.LEFT
    elif car_y >= center_boarder:
        loc = Location.LEFT_LANE
    elif car_y >= right_boarder:
        loc = Location.RIGHT_LANE
    else:
        loc = Location.RIGHT

    return loc


def get_object_location(
    object: state_msgs.msg.TrackedObject, left_line: any, right_line: any
) -> Location:
    """
    Get the location of an object relative to the road lanes.

    The object is classified into one of four zones evaluated at the object's
    center X position:
      - LEFT       : entirely left of the left road border (Y > left_boarder)
      - LEFT_LANE  : left (oncoming) lane between center line and left border
      - RIGHT_LANE : right (ego) lane between right border and center line
      - RIGHT      : entirely right of the right road border (Y < right_boarder)

    An object is considered ON a lane as soon as any part of its bounding box
    (width in Y) overlaps that lane's Y interval.  When the box spans both lanes
    the lane containing the object's center Y is returned.

    Coordinate convention: X forward, Y to the left.

    Arguments:
        object    -- TrackedObject with position_x, position_y (ground-plane
                     centre) and width (Y-extent of the bounding box)
        left_line  -- callable parabola for the left lane line  (higher Y)
        right_line -- callable parabola for the right lane line (lower Y)

    Returns:
        Location -- LEFT, LEFT_LANE, RIGHT_LANE, RIGHT, or UNKNOWN
    """
    location, _ = get_object_location_debug(object, left_line, right_line)
    return location


def get_object_location_debug(
    object: state_msgs.msg.TrackedObject, left_line: any, right_line: any
) -> tuple[Location, dict]:
    """
    Like get_object_location but also returns a dict of intermediate debug values.

    Returns:
        (Location, debug_dict) where debug_dict contains:
            cx, cy, half_w,
            obj_y_left, obj_y_right,
            left_boarder, center_boarder, right_boarder,
            on_left_lane, on_right_lane
    """
    if left_line is None or right_line is None:
        return Location.UNKNOWN, {}

    cx = object.position_x
    cy = object.position_y
    half_w = object.width / 2

    obj_y_left = cy + half_w
    obj_y_right = cy - half_w

    left_boarder, center_boarder, right_boarder = get_boarders(
        left_line, right_line, cx
    )

    on_left_lane = bool(obj_y_left > center_boarder and obj_y_right < left_boarder)
    on_right_lane = bool(obj_y_left > right_boarder and obj_y_right < center_boarder)

    debug = {
        "cx": round(float(cx), 1),
        "cy": round(float(cy), 1),
        "half_w": round(float(half_w), 1),
        "obj_y_left": round(float(obj_y_left), 1),
        "obj_y_right": round(float(obj_y_right), 1),
        "left_boarder": round(float(left_boarder), 1),
        "center_boarder": round(float(center_boarder), 1),
        "right_boarder": round(float(right_boarder), 1),
        "on_left_lane": on_left_lane,
        "on_right_lane": on_right_lane,
    }

    if on_left_lane and on_right_lane:
        location = Location.LEFT_LANE if cy >= center_boarder else Location.RIGHT_LANE
    elif on_left_lane:
        location = Location.LEFT_LANE
    elif on_right_lane:
        location = Location.RIGHT_LANE
    elif cy >= left_boarder:
        location = Location.LEFT
    else:
        location = Location.RIGHT

    return location, debug


def get_distance_to_line(start: tuple[float, float], end: tuple[float, float]) -> float:
    """
    Get the distance from the car to a line defined by two points.

    Arguments:
        start -- start point of the line (x, y)
        end -- end point of the line (x, y
    Returns:
        float -- distance from the car to the line
    """
    # Line coefficients A, B, C for the line equation Ax + By + C = 0
    A = end[1] - start[1]
    B = start[0] - end[0]
    C = end[0] * start[1] - start[0] * end[1]

    # Distance from the car (at origin) to the line
    distance = abs(C) / np.sqrt(A**2 + B**2)
    return distance
