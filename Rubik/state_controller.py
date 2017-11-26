import threading
import time

from RubikGui import main_gui as Gui
from RubikSolver.rubik_solver import RubikSolver
from SimonSays.simon_says import SimonSays
from . import utils

STATE_EXIT = -1
STATE_HOME = 00

STATE_TIMER_HOME = 10
STATE_TIMER_READY = 11
STATE_TIMER_RUNNING = 12
STATE_TIMER_CONFIRM = 13
STATE_TIMER_UPDATE = 14

STATE_MATCH_HOME = 20
STATE_MATCH_READY = 21
STATE_MATCH_SUCCESS = 22
STATE_MATCH_FAILURE = 23
STATE_MATCH_DISPLAY = 24
STATE_MATCH_WAITING = 25
STATE_MATCH_CHECK = 26
STATE_MATCH_UPDATE = 27
STATE_MATCH_CONTINUE = 28

STATE_SIMON_HOME = 30
STATE_SIMON_PLAYING = 31
STATE_SIMON_UPDATE = 32

STATE_RESET = 90
STATE_RESET_CONFIRMED = 91

STATE_STRINGS = {
    STATE_EXIT: "EXIT",
    STATE_HOME: "HOME",
    STATE_TIMER_HOME: "TIMER HOME",
    STATE_TIMER_READY: "TIMER READY",
    STATE_TIMER_RUNNING: "TIMER RUNNING",
    STATE_TIMER_CONFIRM: "TIMER CONFIRM",
    STATE_TIMER_UPDATE: "TIMER UPDATE",
    STATE_MATCH_HOME: "MATCH HOME",
    STATE_MATCH_READY: "MATCH READY",
    STATE_MATCH_SUCCESS: "MATCH SUCCESS",
    STATE_MATCH_FAILURE: "MATCH FAILURE",
    STATE_MATCH_DISPLAY: "MATCH DISPLAY",
    STATE_MATCH_WAITING: "MATCH WAITING",
    STATE_MATCH_CHECK: "MATCH CHECK",
    STATE_MATCH_UPDATE: "MATCH UPDATE",
    STATE_MATCH_CONTINUE: "MATCH CONTINUE",
    STATE_SIMON_HOME: "SIMON HOME",
    STATE_SIMON_PLAYING: "SIMON PLAYING",
    STATE_SIMON_UPDATE: "SIMON UPDATE"
}

STATE_TO_UI = {
    STATE_HOME: Gui.UI_HOME,
    STATE_TIMER_HOME: Gui.UI_TIMER_HOME,
    STATE_TIMER_READY: Gui.UI_TIMER_READY,
    STATE_TIMER_RUNNING: Gui.UI_TIMER_RUNNING,
    STATE_TIMER_CONFIRM: Gui.UI_TIMER_CONFIRM,
    STATE_MATCH_HOME: Gui.UI_MATCH_HOME,
    STATE_MATCH_READY: Gui.UI_MATCH_READY,
    STATE_MATCH_SUCCESS: Gui.UI_MATCH_SUCCESS,
    STATE_MATCH_FAILURE: Gui.UI_MATCH_FAILURE,
    STATE_SIMON_HOME: Gui.UI_SIMON_HOME,
    STATE_SIMON_PLAYING: Gui.UI_SIMON_PLAYING
}

EVENT_DEFAULT = 0
EVENT_BUTTON1 = 1
EVENT_BUTTON2 = 2
EVENT_BUTTON3 = 3
EVENT_BUTTON4 = 4
EVENT_BUTTON5 = 5
EVENT_CUBE_LIFT = 6
EVENT_CUBE_SET = 7
EVENT_SUCCESS = 8
EVENT_FAILURE = 9
EVENT_BUTTON_RESET = -1

EVENT_STRINGS = {
    EVENT_DEFAULT: "DEFAULT",
    EVENT_BUTTON1: "BUTTON1",
    EVENT_BUTTON2: "BUTTON2",
    EVENT_BUTTON3: "BUTTON3",
    EVENT_BUTTON4: "BUTTON4",
    EVENT_BUTTON5: "BUTTON5",
    EVENT_CUBE_LIFT: "CUBE LIFT",
    EVENT_CUBE_SET: "CUBE SET",
    EVENT_SUCCESS: "SUCCESS",
    EVENT_FAILURE: "FAILURE",
    EVENT_BUTTON_RESET: "RESET"
}

TRANSITION_MAP = {
    STATE_HOME: {
        EVENT_BUTTON1: STATE_TIMER_HOME,
        EVENT_BUTTON2: STATE_MATCH_HOME,
        EVENT_BUTTON3: STATE_SIMON_HOME,
        EVENT_BUTTON_RESET: STATE_RESET
    },
    STATE_TIMER_HOME: {
        EVENT_BUTTON1: STATE_TIMER_READY,
        EVENT_BUTTON3: STATE_HOME
    },
    STATE_TIMER_READY: {
        EVENT_CUBE_LIFT: STATE_TIMER_RUNNING,
        EVENT_BUTTON3: STATE_TIMER_HOME
    },
    STATE_TIMER_RUNNING: {
        EVENT_CUBE_SET: STATE_TIMER_CONFIRM,
        EVENT_BUTTON3: STATE_TIMER_HOME
    },
    STATE_TIMER_CONFIRM: {
        EVENT_BUTTON1: STATE_TIMER_UPDATE,
        EVENT_BUTTON3: STATE_TIMER_HOME
    },
    STATE_TIMER_UPDATE: {
        EVENT_DEFAULT: STATE_TIMER_HOME
    },
    STATE_MATCH_HOME: {
        EVENT_BUTTON1: STATE_MATCH_READY,
        EVENT_BUTTON3: STATE_HOME
    },
    STATE_MATCH_READY: {
        EVENT_CUBE_LIFT: STATE_MATCH_DISPLAY,
        EVENT_BUTTON3: STATE_MATCH_HOME
    },
    STATE_MATCH_DISPLAY: {
        EVENT_DEFAULT: STATE_MATCH_WAITING,
        EVENT_BUTTON3: STATE_MATCH_HOME
    },
    STATE_MATCH_WAITING: {
        EVENT_CUBE_SET: STATE_MATCH_CHECK,
        EVENT_BUTTON3: STATE_MATCH_HOME
    },
    STATE_MATCH_CHECK: {
        EVENT_SUCCESS: STATE_MATCH_UPDATE,
        EVENT_FAILURE: STATE_MATCH_CONTINUE
    },
    STATE_MATCH_UPDATE: {
        EVENT_DEFAULT: STATE_MATCH_HOME
    },
    STATE_MATCH_CONTINUE: {
        EVENT_CUBE_LIFT: STATE_MATCH_DISPLAY,
        EVENT_BUTTON3: STATE_MATCH_HOME
    },
    STATE_SIMON_HOME: {
        EVENT_BUTTON1: STATE_SIMON_PLAYING,
        EVENT_BUTTON3: STATE_HOME
    },
    STATE_SIMON_PLAYING: {
        EVENT_SUCCESS: STATE_SIMON_PLAYING,
        EVENT_FAILURE: STATE_SIMON_UPDATE
    },
    STATE_SIMON_UPDATE: {
        EVENT_DEFAULT: STATE_SIMON_HOME
    }
}


def get_state_string(state):
    return STATE_STRINGS.get(state, "UNKNOWN STATE")


def get_event_string(event):
    return EVENT_STRINGS.get(event, "UNKNOWN EVENT")


# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class StateController (threading.Thread, Gui.Callback):

    _state = STATE_HOME
    _ui_state = Gui.UI_HOME
    _needs_update = False

    _gui = None
    _solver = None
    _simon = None

    def __init__(self, gui, solver, simon):
        self._gui = gui
        self._solver = solver
        self._simon = simon
        self._gui.set_ui_state(Gui.UI_HOME)

    def get_ui_for_state(self):
        return STATE_TO_UI.get(self._state, self._ui_state)

    def on_press(self, which):
        self.handle_event(which)

    def handle_event(self, event):
        print("Handling event " + get_event_string(event))
        curr_state = self._state
        next_state = TRANSITION_MAP.get(curr_state).get(event, curr_state)
        if next_state == curr_state:
            print("No transition from " + get_state_string(curr_state)
                  + " on event " + get_event_string(event))
            return
        self.transition(curr_state, next_state)

    def transition(self, from_state, to_state):
        print("Transitioning from " + get_state_string(from_state)
              + " to " + get_state_string(to_state))
        self._state = to_state
        self._needs_update = True

    def run(self):
        print("Running state controller!")
        while True:
            if self._state == STATE_EXIT:
                self._gui.exit()
                break
            if self._needs_update:
                next_ui = self.get_ui_for_state()
                if next_ui != self._ui_state:
                    self._gui.set_ui_state(next_ui)
                    self._ui_state = next_ui
                    print("Updated UI to " + str(next_ui))
                self._needs_update = False

            print("Enter (q)uit or 0-9 for events")
            key = utils.getChar()
            if key.upper() == 'Q':
                self._state = STATE_EXIT
            else:
                event = key - '0'
                self.handle_event(int(event))

        return

