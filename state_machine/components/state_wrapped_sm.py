import threading
import time

import yasmin
import yasmin_viewer

from state_machine.components.base_state import BaseState
from state_machine.components.state_description import BlackBoard


class StateWrappedStateMachine(BaseState):
    """Concurrent state for Smarty."""

    NAME = "concurrent"
    TRANSITIONS = {}

    def __init__(self, state_classes: list[BaseState], debug: bool = False):
        """Initialize the state."""
        self.TRANSITIONS["loop"] = self.NAME
        super().__init__()
        self.debug = debug
        self._init_state_machine(state_classes)
        self._run_sm = False
        self._first_call = True
        self._timer = None
        self._sm_thread = None
        self._sm_watchdog = None
        self._outcome = None

    def reset(self):
        """Reset the state."""
        if self._run_sm:
            yasmin.YASMIN_LOG_WARN("State machine is running, cannot reset")
            return
        self._sm_thread = None
        self._sm_watchdog = None
        self._run_sm = False
        if self._timer is not None and self._timer.is_alive():
            self._timer.cancel()
        self._timer = None
        self._outcome = None

    def local_execute(
        self,
        timeout_time: float = -1.0,
    ) -> str:
        """
        Execute the state and start the state machine.

        Arguments:
            timeout_time -- Timeout in seconds (default: -1.0, no timeout)

        Returns:
            str -- Next state (loop) per default
        """
        super().local_execute(update_black_board=False)
        if self._first_call:
            self.reset()
            # self.blackboard.current_state = self.NAME
            if timeout_time > 0:
                self.start_timeout_timer(timeout_time)
            self._first_call = False
            self._start_sm()

        while self._run_sm:
            time.sleep(0.0001)

        self._first_call = True
        return self._outcome

    def stop(self):
        """Stop the state machine."""
        if self._run_sm:
            self._run_sm = False
            self.sm.cancel_state()
            self._sm_watchdog.join()
            self._sm_thread.join()
            self._first_call = True
        else:
            yasmin.YASMIN_LOG_WARN("Tried to Stop but State machine not running")

    def _start_sm(self):
        """Start the state machine."""
        if self._run_sm:
            yasmin.YASMIN_LOG_WARN("State machine already running")
            return
        yasmin.YASMIN_LOG_INFO("Starting internal state machine")
        self._run_sm = True
        self._sm_thread = threading.Thread(target=self._sm_thread_fun)
        self._sm_watchdog = threading.Thread(target=self._sm_watchdog_fun)
        self._sm_thread.start()
        self._sm_watchdog.start()

    def _sm_thread_fun(self):
        """Run the state machine."""
        if self.blackboard is None:
            raise ValueError("Blackboard is not set")

        self._run_sm = True
        self._outcome = self.sm()
        yasmin.YASMIN_LOG_WARN("Internal State Machine finished!")
        self._run_sm = False

    def _sm_watchdog_fun(self):
        """Watchdog for the state machine."""
        while self._run_sm:
            time.sleep(0.0001)
        if self.sm.is_running:
            self.sm.cancel_state()
            yasmin.YASMIN_LOG_WARN("State machine Cancelled")

    def _init_state_machine(self, state_classes: list[yasmin.State]) -> None:
        """
        Initialize the state machine.

        Arguments:
            state_classes -- List of state classes
        """
        self.sm = yasmin.StateMachine(outcomes=["done", "canceled"])
        [self._add_state(state_class) for state_class in state_classes]

    def _add_state(self, state_class: yasmin.State):
        """
        Add a state to the state machine.

        Arguments:
            state_class -- State Class
        """
        state: yasmin.State = state_class(self.debug)
        self.sm.add_state(name=state.NAME, state=state, transitions=state.TRANSITIONS)

    def cancel_state(self):
        """Cancel the state machine."""
        self._outcome = "canceled"
        self.sm.cancel_state()
        self.stop()
        return super().cancel_state()

    def start_timeout_timer(self, timeout: float):
        """Set the timeout for the state machine."""
        # Start timer to cancel state machine after timeout in seconds
        if timeout > 0:
            self._timer = threading.Timer(timeout, self.cancel_state)
            self._timer.start()
            yasmin.YASMIN_LOG_WARN("Canceld with timer.")
