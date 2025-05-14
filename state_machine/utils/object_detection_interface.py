import numpy as np
from smarty_utils.enums import OBJECTS, SIGNS
from state_machine.utils.detectors import get_object_location
import std_msgs.msg



def _parse_float32_multiarray(msg: std_msgs.msg.Float32MultiArray):
    """Parse the Float32MultiArray message."""
    assert isinstance(msg, std_msgs.msg.Float32MultiArray), "Invalid message type"
    result = [msg.data[i] for i in range(len(msg.data))]
    # Split in groups of 6
    result = [
        result[i : i + 6] for i in range(0, len(result), 6)
    ]
    if len(result) <= 0:
        return []
    if not isinstance(result[0], list):
        result = [result]
    return result

def _calc_dist(obj_position: dict) -> float:
    """Calculate the distance from the car to the object."""
    assert isinstance(obj_position, dict), "Invalid object position type"
    x = obj_position["bottom_left_x"]
    y = obj_position["bottom_left_y"]
    left = np.linalg.norm([x, y])
    x = obj_position["bottom_right_x"]
    y = obj_position["bottom_right_y"]
    right = np.linalg.norm([x, y])
    return min(left, right)

def create_obj_sign(msg: std_msgs.msg.Float32MultiArray, is_object: bool, parent: any) -> list[dict]:
    """
    Create a list of objects or signs from std_msgs.msg.Float32MultiArray.

    Arguments:
        msg -- std_msgs.msg.Float32MultiArray message
        is_object -- True if the data is for objects, False if for signs
        parent -- Parent object to access blackboard

    Returns:
        list of objects or signs
    """
    parsed = _parse_float32_multiarray(msg)
    results = []
    for obj in parsed:
        len(obj) >= 6, "Invalid object data"
        obj_id = obj[0]
        obj_position = {
            "bottom_left_x": obj[1],
            "bottom_left_y": obj[2],
            "bottom_right_x": obj[3],
            "bottom_right_y": obj[4],
        }
        left_lane = parent.blackboard.lane_coefficients.get("left", None)
        right_lane = parent.blackboard.lane_coefficients.get("right", None)
        obj_location = get_object_location(obj_position, left_lane, right_lane)
        obj_dist = _calc_dist(obj_position)
        obj_name = OBJECTS(obj_id) if is_object else SIGNS(obj_id)
        results.append(
            {
                "id": obj_id,
                "position": obj_position,
                "distance": obj_dist,
                "location": obj_location,
                "name": obj_name,
                "timestamp": parent.get_clock().now().nanoseconds,
            }
        )
    return results