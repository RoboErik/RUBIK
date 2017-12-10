import threading
import time, cPickle, math
from Queue import *

from RubikGui import main_gui as Gui
from RubikSolver import rubik_solver as Solver
from SimonSays import simon_says as Simon
from . import utils
from . import queue_common
from event import *
import sounds

Command = queue_common.Command

STATE_EXIT = -1
STATE_HOME = 00

STATE_TIMER_HOME = 10
STATE_TIMER_READY = 11
STATE_TIMER_PLAYING = 12
STATE_TIMER_CONFIRM = 13
STATE_TIMER_UPDATE = 14

STATE_MATCH_HOME = 20
STATE_MATCH_READY = 21
STATE_MATCH_PLAYING = 22

STATE_SIMON_HOME = 30
STATE_SIMON_READY = 31
STATE_SIMON_PLAYING = 32

STATE_RESET = 90

STATE_STRINGS = {
    STATE_EXIT: "EXIT",
    STATE_HOME: "HOME",
    STATE_TIMER_HOME: "TIMER HOME",
    STATE_TIMER_READY: "TIMER READY",
    STATE_TIMER_PLAYING: "TIMER RUNNING",
    STATE_TIMER_CONFIRM: "TIMER CONFIRM",
    STATE_TIMER_UPDATE: "TIMER UPDATE",
    STATE_MATCH_HOME: "MATCH HOME",
    STATE_MATCH_READY: "MATCH READY",
    STATE_MATCH_PLAYING: "MATCH PLAYING",
    STATE_SIMON_HOME: "SIMON HOME",
    STATE_SIMON_PLAYING: "SIMON PLAYING",
    STATE_RESET: "RESET"
}

STATE_TO_UI = {
    STATE_HOME: Gui.UI_HOME,
    STATE_TIMER_HOME: Gui.UI_TIMER_HOME,
    STATE_TIMER_READY: Gui.UI_TIMER_READY,
    STATE_TIMER_PLAYING: Gui.UI_TIMER_RUNNING,
    STATE_TIMER_CONFIRM: Gui.UI_TIMER_CONFIRM,
    STATE_MATCH_HOME: Gui.UI_MATCH_HOME,
    STATE_MATCH_READY: Gui.UI_MATCH_READY,
    STATE_MATCH_PLAYING: Gui.UI_MATCH_PLAYING,
    STATE_SIMON_HOME: Gui.UI_SIMON_HOME,
    STATE_SIMON_PLAYING: Gui.UI_SIMON_PLAYING,
    STATE_RESET: Gui.UI_CONFIRM_RESET
}

TRANSITION_MAP = {
    STATE_HOME: {
        EVENT_BUTTON1: STATE_TIMER_HOME,
        EVENT_BUTTON3: STATE_MATCH_HOME,
        EVENT_BUTTON2: STATE_SIMON_HOME,
        EVENT_BUTTON_RESET: STATE_RESET
    },
    STATE_TIMER_HOME: {
        EVENT_BUTTON1: STATE_TIMER_READY,
        EVENT_BUTTON2: STATE_HOME
    },
    STATE_TIMER_READY: {
        EVENT_UPDATE: STATE_TIMER_PLAYING,
        EVENT_BUTTON2: STATE_TIMER_HOME
    },
    STATE_TIMER_PLAYING: {
        EVENT_SUCCESS: STATE_TIMER_CONFIRM,
        EVENT_BUTTON2: STATE_TIMER_HOME
    },
    STATE_TIMER_CONFIRM: {
        EVENT_BUTTON1: STATE_TIMER_HOME,
        EVENT_BUTTON2: STATE_TIMER_HOME
    },
    STATE_MATCH_HOME: {
        EVENT_BUTTON1: STATE_MATCH_READY,
        EVENT_BUTTON2: STATE_HOME
    },
    STATE_MATCH_READY: {
        EVENT_UPDATE: STATE_MATCH_PLAYING,
        EVENT_BUTTON2: STATE_MATCH_HOME
    },
    STATE_MATCH_PLAYING: {
        EVENT_SUCCESS: STATE_MATCH_HOME,
        EVENT_FAILURE: STATE_MATCH_HOME,
        EVENT_BUTTON2: STATE_MATCH_HOME
    },
    STATE_SIMON_HOME: {
        EVENT_BUTTON1: STATE_SIMON_PLAYING,
        EVENT_BUTTON2: STATE_HOME
    },
    STATE_SIMON_PLAYING: {
        EVENT_SUCCESS: STATE_SIMON_PLAYING,
        EVENT_FAILURE: STATE_SIMON_HOME
    },
    STATE_RESET: {
        EVENT_BUTTON2: STATE_HOME,
        EVENT_BUTTON_RESET: STATE_HOME
    }
}

RESET_DETECT_WINDOW = 0.5

def get_state_string(state):
    return STATE_STRINGS.get(state, "UNKNOWN STATE")


def get_event_string(event):
    return EVENT_STRINGS.get(event, "UNKNOWN EVENT")


def get_source_string(source):
    return SOURCE_STRINGS.get(source, "UNKNOWN SOURCE")


def s_to_time_string(secs):
    mins = math.floor(secs / 60)
    seconds = float(round(secs * 100) % 6000) / 100.0
    return "%02d:%04.2f" % (mins, seconds)


# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class StateController (threading.Thread):

    def __init__(self, gui, solver, simon):
        self._in_game = False
        self._state = STATE_HOME
        self._ui_state = Gui.UI_HOME
        self._temp_data = None
        self._reset_timer = None
        self._reset_buttons = None

        self._event_queue = Queue()

        self._gui = gui
        self._gui_queue = gui.get_queue()
        gui.set_event_queue(self._event_queue)

        self._solver = solver
        self._solver_queue = solver.get_queue()
        solver.set_event_queue(self._event_queue)
        solver.start()

        self._simon = simon
        self._simon_queue = simon.get_queue()
        simon.set_event_queue(self._event_queue)
        simon.start()

        self._gui.set_ui_state(Gui.UI_HOME)
        self._scores = None
        self.load_scores()

        self._sounds = sounds.Sounds()

        threading.Thread.__init__(self)

    def load_scores(self):
        try:
            score_file = open("puzzle_scores.txt", mode='r')
            self._scores = cPickle.load(score_file)
        except IOError:
            print("Score file not created yet")
            self._scores = {
                "time": 3599.99, #59:59.99
                "match": 3599.99,
                "simon": 0,
                "gears": False
            }

    def save_scores(self):
        score_file = open("puzzle_scores.txt", mode='w')
        cPickle.dump(self._scores, score_file)

    def get_ui_for_state(self):
        return STATE_TO_UI.get(self._state, self._ui_state)

    def check_queue(self):
        got_event = True
        while got_event:
            try:
                event = self._event_queue.get(False)
                self.handle_event(event)
                self._event_queue.task_done()
            except Empty:
                got_event = False

    def handle_event(self, event):
        if event.event != EVENT_UPDATE:
            print("Handling event " + get_event_string(event.event)
                  + " from " + get_source_string(event.source))
        curr_state = self._state
        next_state = TRANSITION_MAP.get(curr_state).get(event.event, curr_state)

        self.check_for_reset(curr_state, event)

        if event.source == SOURCE_SIMON and event.event == EVENT_FAILURE:
            self._sounds.play_sound(sounds.BUZZ)
            if event.data > self._scores["simon"]:
                self._scores["simon"] = event.data
                self.save_scores()
        if event.source == SOURCE_SIMON and event.event == EVENT_UPDATE:
            if curr_state == STATE_SIMON_PLAYING:
                data1 = str(self._scores["simon"])
                data2 = str(event.data)
                self._gui_queue.put(Command(Gui.UI_SIMON_PLAYING, data1, data2))
        if event.source == SOURCE_SIMON and event.event == EVENT_PLAY_SOUND:
            duration = 1500
            if event.data2 is not None:
                duration = int(event.data2 * 1000)
            self._sounds.play_button(event.data, duration)

        if event.source == SOURCE_MATCH and event.event == EVENT_SUCCESS:
            if event.data < self._scores["match"]:
                self._scores["match"] = event.data
                self.save_scores()
        if event.source == SOURCE_MATCH and event.event == EVENT_UPDATE:
            if curr_state == STATE_MATCH_PLAYING or curr_state == STATE_MATCH_READY:
                data1 = s_to_time_string(self._scores["match"])
                data2 = s_to_time_string(event.data)
                self._gui_queue.put(Command(Gui.UI_MATCH_PLAYING, data1, data2))

        if event.source == SOURCE_TIMER and event.event == EVENT_SUCCESS:
            if self._temp_data < self._scores["time"]:
                self._temp_data = event.data
            else:
                # Not a better score, skip confirming
                print("Worse timer score, skipping confirmation step.")
                next_state = STATE_TIMER_HOME
        if event.event == EVENT_BUTTON1 and curr_state == STATE_TIMER_CONFIRM:
            if self._temp_data < self._scores["time"]:
                self._scores["time"] = self._temp_data
                self.save_scores()
        if event.source == SOURCE_TIMER and event.event == EVENT_UPDATE:
            if curr_state == STATE_TIMER_PLAYING or curr_state == STATE_TIMER_READY:
                data1 = s_to_time_string(self._scores["time"])
                data2 = s_to_time_string(event.data)
                self._gui_queue.put(Command(Gui.UI_TIMER_RUNNING, data1, data2))

        if next_state == curr_state:
            return
        self.transition(curr_state, next_state)

    def check_for_reset(self, curr_state, event):
        # If buttons 4 and 5 are pressed within .5s of each other trigger the reset screen
        if curr_state == STATE_HOME:
            if event.event == EVENT_BUTTON4 or event.event == EVENT_BUTTON5:
                if self._reset_timer is None:
                    self._reset_buttons = None
                elif time.time() - self._reset_timer > RESET_DETECT_WINDOW:
                    self._reset_buttons = None

                if self._reset_buttons is None or self._reset_buttons[0] == event.event:
                    self._reset_buttons = [event.event]
                    self._reset_timer = time.time()
                else:
                    self._event_queue.put(Event(SOURCE_OTHER, EVENT_BUTTON_RESET))
                    self._reset_buttons = None
                    self._reset_timer = None

        if curr_state == STATE_RESET:
            if event.event == EVENT_BUTTON3 \
                    or event.event == EVENT_BUTTON4 \
                    or event.event == EVENT_BUTTON5:
                if self._reset_timer is None:
                    self._reset_buttons = None
                elif time.time() - self._reset_timer > RESET_DETECT_WINDOW:
                    self._reset_buttons = None

                if self._reset_buttons is None:
                    self._reset_buttons = [event.event]
                    self._reset_timer = time.time()
                else:
                    found = False
                    for i in range(len(self._reset_buttons)):
                        if self._reset_buttons[i] == event.event:
                            found = True
                            break
                    if not found:
                        if len(self._reset_buttons) == 2:
                            # This is the third reset button.
                            self._event_queue.put(Event(SOURCE_OTHER, EVENT_BUTTON_RESET))
                            self._reset_buttons = None
                            self._reset_timer = None
                        else:
                            self._reset_buttons.append(event.event)

        if curr_state == STATE_RESET and event.event == EVENT_BUTTON_RESET:
            self._scores = {
                "time": 3599.99,  # 59:59.99
                "match": 3599.99,
                "simon": 0,
                "gears": False
            }
            self.save_scores()

    def transition(self, from_state, to_state):
        if from_state == to_state:
            return
        print("Transitioning from " + get_state_string(from_state)
              + " to " + get_state_string(to_state))
        if from_state == STATE_SIMON_PLAYING:
            self._simon_queue.put(Command(Simon.COMMAND_CHANGE_MODE, Simon.MODE_LISTENING))
            self._in_game = False
        if from_state == STATE_TIMER_READY:
            if to_state != STATE_TIMER_PLAYING:
                self._solver_queue.put(Command(Solver.COMMAND_SET_MODE, Solver.MODE_IDLE))
                self._in_game = False
        if from_state == STATE_TIMER_PLAYING:
            self._solver_queue.put(Command(Solver.COMMAND_SET_MODE, Solver.MODE_IDLE))
            self._in_game = False
        if from_state == STATE_MATCH_READY:
            if to_state != STATE_MATCH_PLAYING:
                self._solver_queue.put(Command(Solver.COMMAND_SET_MODE, Solver.MODE_IDLE))
                self._in_game = False
        if from_state == STATE_MATCH_PLAYING:
            self._solver_queue.put(Command(Solver.COMMAND_SET_MODE, Solver.MODE_IDLE))
            self._in_game = False

        if to_state == STATE_SIMON_PLAYING:
            self._simon_queue.put(Command(Simon.COMMAND_CHANGE_MODE, Simon.MODE_PLAYING))
            self._in_game = True
        if to_state == STATE_MATCH_READY:
            self._solver_queue.put(Command(Solver.COMMAND_SET_MODE, Solver.MODE_PATTERN))
            self._in_game = True
        if to_state == STATE_TIMER_READY:
            self._solver_queue.put(Command(Solver.COMMAND_SET_MODE, Solver.MODE_TIME))
            self._in_game = True

        self._state = to_state
        next_ui = self.get_ui_for_state()
        print("Next ui: " + str(next_ui) + ", Curr ui:" + str(self._ui_state))
        if next_ui != self._ui_state:
            data1 = ""
            data2 = ""
            if next_ui == Gui.UI_MATCH_HOME:
                data1 = s_to_time_string(self._scores["match"])
            elif next_ui == Gui.UI_MATCH_READY:
                data1 = s_to_time_string(self._scores["match"])
                data2 = "00:00.00"
                # MATCH_PLAYING is updated from the event
            elif next_ui == Gui.UI_TIMER_HOME:
                data1 = s_to_time_string(self._scores["time"])
            elif next_ui == Gui.UI_TIMER_READY:
                data1 = s_to_time_string(self._scores["time"])
                data2 = "00:00.00"
                # TIMER_PLAYING is updated from the event
            elif next_ui == Gui.UI_SIMON_HOME:
                data1 = str(self._scores["simon"])
            elif next_ui == Gui.UI_SIMON_PLAYING:
                data1 = "0"
            elif next_ui == Gui.UI_TIMER_CONFIRM:
                data1 = s_to_time_string(self._scores["time"])
                data2 = s_to_time_string(self._temp_data)

            command = Command(next_ui, data1, data2)
            self._gui_queue.put(command)
            self._ui_state = next_ui
            print("Updated UI to " + str(next_ui))

    def run(self):
        print("Running state controller!")
        self._sounds.prepare()
        self._sounds.play_sound(sounds.BLOOP)
        while True:
            if self._state == STATE_EXIT:
                self._gui_queue.put(Command(Gui.UI_QUIT))
                self._simon_queue.put(Command(Simon.COMMAND_QUIT))
                break
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
                    self._sounds.play_sound(sounds.BLOOP)

            self.check_queue()
        self._sounds.cleanup()
