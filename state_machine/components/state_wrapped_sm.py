import threading
import time

import yasmin
import yasmin_viewer

from state_machine.components.base_state import BaseState


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
        self.reset()

    def reset(self):
        """Reset the state."""
        if self._run_sm:
            yasmin.YASMIN_LOG_WARN("State machine is running, cannot reset")
            return
        self.blackboard = None
        self._sm_thread = None
        self._sm_watchdog = None
        self._run_sm = False

    def execute(self, blackboard: yasmin.Blackboard) -> str:
        """
        Execute the state and start the state machine.

        Arguments:
            blackboard -- Blackboard object

        Returns:
            str -- Next state (loop) per default
        """
        super().execute(blackboard)
        if self._first_call:
            self.reset()
            self.blackboard = blackboard
            self._first_call = False
            self._start_sm()
            return "loop"

        if self._run_sm:
            return "loop"

        self._first_call = True
        return self._outcome

    def stop(self):
        """Stop the state machine."""
        if self._run_sm:
            self._run_sm = False
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
        self._outcome = self.sm(self.blackboard)
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

        if self.debug:
            yasmin_viewer.YasminViewerPub(f"{self.NAME}_state_machine", self.sm)

    def _add_state(self, state_class: yasmin.State):
        """
        Add a state to the state machine.

        Arguments:
            state_class -- State Class
        """
        state: yasmin.State = state_class(self.debug)
        self.sm.add_state(name=state.NAME, state=state, transitions=state.TRANSITIONS)
