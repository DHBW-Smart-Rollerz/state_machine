from smarty_utils.enums import OBJECTS, SIGNS, Location


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
