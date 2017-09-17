import threading
import RPi.GPIO as GPIO
from . import switch_timer
from .. import utils
from .. import pins


# In this mode just records the time between lifting and replacing the Cube.
MODE_TIME = 0
# In this mode generates a pattern and checks for that pattern on down.
MODE_PATTERN = 1

# Does not solve a Rubik cube, but either times how long it took to solve or
# requires a specific pattern be created.
class RubikSolver (threading.Thread):

    _state = 0
    _mode = MODE_TIME
    _pattern = []
    _result = []

    _timer = switch_timer.SwitchTimer()
    _stop_event = threading.Event()

    def set_mode(self, mode):
        _mode = mode

    def show_pattern(self):
        return

    def hide_pattern(self):
        return

    def _switch_callback(self, channel):
        if GPIO.input(pins.RUBIK_CUBE_SWITCH):
            if (self._mode == MODE_PATTERN):
                self.show_pattern()
            self._timer.on_switch_up()
        else:
            self._timer.on_switch_down()

    def _setup(self):
        print("Setup of RubikSolver")
        GPIO.add_event_detect(pins.RUBIK_CUBE_SWITCH, GPIO.BOTH, callback=self._switch_callback, bouncetime=300)

    def _teardown(self):
        print("Teardown of RubikSolver")
        GPIO.remove_event_detect(pins.RUBIK_CUBE_SWITCH)
        self.hide_pattern()

    def stop(self):
        print("Stopping RubikSolver! Time is " + str(utils.milli_time()))
        self._stop_event.set()

    def run(self):
        self._setup()
        self._stop_event.wait(6)
        self._teardown()
