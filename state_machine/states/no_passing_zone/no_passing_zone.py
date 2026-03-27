import time

from smarty_utils.enums import OBJECTS, SIGNS, Light, Location

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard, StateDescription
from state_machine.states.no_passing_zone import NO_PASSING_ZONE_CONSTANTS
from state_machine.utils.detectors import check_dist_to_obj_sign, dist_to_obj_sign


class NoPassingZoneState(BaseState):
    """
    No-passing zone state.

    The car must stay in the right lane and follow any vehicle ahead without
    overtaking.  The state ends when:
      - a NO_OVERTAKING_LIFTED sign is detected within range, OR
      - the timeout expires (fallback to driving)
    """

    NAME = "no_passing_zone"
    STATE_DESCRIPTION = StateDescription(
        light_configuration=Light.NORMAL,
        max_speed=NO_PASSING_ZONE_CONSTANTS.CRUISE_SPEED,
        goal_lane=Location.RIGHT_LANE,
    )

    def __init__(self, debug: bool = False):
        """Initializes the NoPassingZoneState."""
        from state_machine.states.drive.driving import DrivingState

        self.TRANSITIONS = {
            "done": DrivingState.NAME,
        }
        super().__init__(debug)

    def local_execute(self, blackboard: BlackBoard) -> str:
        """
        Execute the no-passing zone state.

        Follows any vehicle detected ahead in the ego lane at a safe distance.
        Stays in the right lane at all times (no lane changes).
        Exits as soon as a NO_OVERTAKING_LIFTED sign is seen or the timeout fires.

        Arguments:
            blackboard -- The blackboard containing the state information

        Returns:
            str -- Outcome: always "done" (back to DrivingState)
        """
        super().local_execute(blackboard)

        start_time = time.perf_counter()

        while time.perf_counter() - start_time < NO_PASSING_ZONE_CONSTANTS.TIMEOUT:
            # ── Exit condition: no-passing zone has ended ────────────────────
            if check_dist_to_obj_sign(
                self.blackboard.signs,
                [SIGNS.NO_OVERTAKING_LIFTED],
                NO_PASSING_ZONE_CONSTANTS.LIFTED_SIGN_DIST,
                location=Location.NOT_RELEVANT,
            ):
                self.log_state("No-passing zone: lifted sign detected, resuming drive")
                return "done"

            # ── Follow a leading vehicle if one is close enough ──────────────
            vehicle_ahead = check_dist_to_obj_sign(
                self.blackboard.objects,
                [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
                NO_PASSING_ZONE_CONSTANTS.FOLLOW_DIST,
                location=self.blackboard.car_lane,
            )

            if vehicle_ahead:
                dist = dist_to_obj_sign(
                    self.blackboard.objects,
                    [OBJECTS.VEHICLE, OBJECTS.PEDESTRIAN],
                    location=self.blackboard.car_lane,
                )
                # Slow down proportionally as we close in on the safe gap
                gap_error = dist - NO_PASSING_ZONE_CONSTANTS.SAFE_FOLLOWING_DIST
                if gap_error <= 0:
                    # Too close — stop
                    self.blackboard.max_speed = 0.0
                else:
                    # Scale speed between 0 and FOLLOW_SPEED based on remaining gap
                    ratio = min(
                        gap_error / NO_PASSING_ZONE_CONSTANTS.SAFE_FOLLOWING_DIST, 1.0
                    )
                    self.blackboard.max_speed = (
                        NO_PASSING_ZONE_CONSTANTS.FOLLOW_SPEED * ratio
                    )
                self.log_state(
                    f"No-passing zone: following vehicle at {dist:.0f} mm,"
                    f" speed={self.blackboard.max_speed:.2f} m/s"
                )
            else:
                # No vehicle immediately ahead — cruise at zone speed
                self.blackboard.max_speed = NO_PASSING_ZONE_CONSTANTS.CRUISE_SPEED
                self.log_state("No-passing zone: cruising, no vehicle ahead")

            time.sleep(0.01)

        self.log_state("No-passing zone: timeout, resuming drive")
        return "done"
