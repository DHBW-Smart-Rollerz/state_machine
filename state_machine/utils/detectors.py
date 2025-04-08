from state_machine.utils import Location


def check_dist_to_obj_sign(
    objects: list,
    obj_types: str | list[str],
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
    if isinstance(obj_types, str):
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


def opposite_of_location(
    location: Location,
) -> Location:
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
