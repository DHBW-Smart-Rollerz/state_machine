import numpy as np
import state_msgs
import state_msgs.msg
from smarty_utils.enums import OBJECTS, SIGNS

from state_machine.utils.detectors import get_object_location
import yasmin


def _calc_dist(obj_position: dict) -> float:
    """Calculate the distance from the car to the object."""
    assert isinstance(obj_position, dict), "Invalid object position type"
    return np.linalg.norm([obj_position["x"], obj_position["y"]]).astype(float)


def create_obj_sign(msg: state_msgs.msg.State, parent: any) -> list[dict]:
    """
    Create a list of objects or signs from state_msgs.

    The type (OBJECTS vs SIGNS) is determined automatically from obj.class_id:
    if the class_id is a valid OBJECTS value it is treated as a dynamic object,
    otherwise it is treated as a static sign.

    Arguments:
        msg    -- state_msgs.msg.State message containing the tracked objects/signs
        parent -- parent node used to access the blackboard and clock

    Returns:
        list of dicts with keys: id, position, distance, location, name, timestamp
    """
    obj_ids = {e.value for e in OBJECTS}

    results = []
    for obj in msg.tracked_objects:
        assert isinstance(obj, state_msgs.msg.TrackedObject), "Invalid object type"
        obj_id = obj.tracked_id
        obj_position = {"x": obj.position_x, "y": obj.position_y}
        left_lane = parent.blackboard.lane_coefficients.get("left", None)
        right_lane = parent.blackboard.lane_coefficients.get("right", None)
        obj_location = get_object_location(obj, left_lane, right_lane)
        obj_dist = _calc_dist(obj_position)
        obj_name = (
            OBJECTS(int(obj.class_id))
            if int(obj.class_id) in obj_ids
            else SIGNS(int(obj.class_id))
        )
        # yasmin.YASMIN_LOG_INFO(
        #     f"Detected object/sign: id={obj_id}, name={obj_name}, position={obj_position}, distance={obj_dist:.2f}m, location={obj_location}, type={'OBJECT' if isinstance(obj_name, OBJECTS) else 'SIGN'}"
        # )
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
