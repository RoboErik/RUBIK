import threading
import time, cPickle
from Queue import *

from RubikGui import main_gui as Gui
from RubikSolver import rubik_solver as Rubik
from SimonSays import simon_says as Simon
from . import utils
from event import *

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
    STATE_SIMON_PLAYING: "SIMON PLAYING"
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
        EVENT_FAILURE: STATE_SIMON_HOME
    }
}


def get_state_string(state):
    return STATE_STRINGS.get(state, "UNKNOWN STATE")


def get_event_string(event):
    return EVENT_STRINGS.get(event, "UNKNOWN EVENT")


def ms_to_time_string(ms):
    mins = ms / (60 * 1000)
    seconds = (ms / 1000) % 60
    ms = (ms % 1000) / 10  # only get two sig figs
    return "%02d:%02d.%02d" % (mins, seconds, ms)


# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class StateController (threading.Thread):

    _in_game = False
    _scores = None
    _temp_scores = None
    _state = STATE_HOME
    _ui_state = Gui.UI_HOME
    _needs_update = False

    _gui = None
    _gui_queue = None
    _solver = None
    _solver_queue = None
    _simon = None
    _simon_queue = None

    _event_queue = Queue()

    def __init__(self, gui, solver, simon):
        self._gui = gui
        self._gui_queue = gui.get_queue()
        gui.set_event_queue(self._event_queue)

        self._solver = solver

        self._simon = simon
        self._simon_queue = simon.get_queue()
        simon.set_event_queue(self._event_queue)
        simon.start()

        self._gui.set_ui_state(Gui.UI_HOME)
        self.load_scores()
        super(StateController, self).__init__()

    def load_scores(self):
        try:
            score_file = open("puzzle_scores.txt", mode='r')
            self._scores = cPickle.load(score_file)
        except IOError:
            print("Score file not created yet")
            self._scores = {
                "time": 3599990, #59:59.99
                "match": 3599990,
                "simon": 0,
                "gears": False
            }
        self._temp_scores = {
            "time": 3599990,  # 59:59.99
            "match": 3599990,
            "simon": 0,
            "gears": False
        }

    def save_scores(self):
        score_file = open("puzzle_scores.txt", mode='w')
        cPickle.dump(self._scores, score_file)

    def get_ui_for_state(self):
        return STATE_TO_UI.get(self._state, self._ui_state)

    def get_score_string_for_ui(self, ui_state):
        if Gui.UI_TIMER_START <= ui_state <= Gui.UI_TIMER_END:
            return ms_to_time_string(self._scores["time"])
        if Gui.UI_MATCH_START <= ui_state <= Gui.UI_MATCH_END:
            return ms_to_time_string(self._scores["match"])
        if Gui.UI_SIMON_START <= ui_state <= Gui.UI_SIMON_END:
            return str(self._scores["simon"])
        return ""

    def check_queue(self):
        try:
            event = self._event_queue.get(False)
            self.handle_event(event)
            self._event_queue.task_done()
        except Empty:
            pass

    def handle_event(self, event):
        print("Handling event " + get_event_string(event.event))
        if event.source == SOURCE_SIMON and event.event == EVENT_FAILURE:
            if event.data > self._scores["simon"]:
                self._scores["simon"] = event.data
                self.save_scores()
        curr_state = self._state
        next_state = TRANSITION_MAP.get(curr_state).get(event.event, curr_state)
        if next_state == curr_state:
            print("No transition from " + get_state_string(curr_state)
                  + " on event " + get_event_string(event.event))
            return
        self.transition(curr_state, next_state)

    def transition(self, from_state, to_state):
        print("Transitioning from " + get_state_string(from_state)
              + " to " + get_state_string(to_state))
        if to_state == STATE_SIMON_PLAYING:
            self._simon_queue.put(Simon.Command(Simon.COMMAND_CHANGE_MODE, Simon.MODE_PLAYING))
            self._in_game = True
        elif from_state == STATE_SIMON_PLAYING:
            self._simon_queue.put(Simon.Command(Simon.COMMAND_CHANGE_MODE, Simon.MODE_LISTENING))
            self._in_game = False
        self._state = to_state
        self._needs_update = True

    def run(self):
        print("Running state controller!")
        while True:
            if self._state == STATE_EXIT:
                self._gui_queue.put(Gui.UiCommand(Gui.UI_QUIT))
                self._simon_queue.put(Simon.Command(Simon.COMMAND_QUIT))
                break
            if self._needs_update:
                next_ui = self.get_ui_for_state()
                if next_ui != self._ui_state:
                    command = Gui.UiCommand(next_ui, self.get_score_string_for_ui(next_ui))
                    self._gui_queue.put(command)
                    self._ui_state = next_ui
                    print("Updated UI to " + str(next_ui))
                self._needs_update = False

            if self._in_game:
                time.sleep(0.1)
            else:
                print("Enter (q)uit or 0-9 for events")
                key = utils.getChar()
                if key.upper() == 'Q':
                    self._state = STATE_EXIT
                else:
                    event = ord(key) - ord('0')
                    self._event_queue.put(Event(SOURCE_OTHER, event))

            self.check_queue()

        return

