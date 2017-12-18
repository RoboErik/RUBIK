import threading, time
import RPi.GPIO as GPIO

from .. import pins
from .. import utils
from .. import queue_common
from .. import event

COMMAND_QUIT = -1

RESULT_TOO_LOW = 1
RESULT_TOO_HIGH = 2
RESULT_JUST_RIGHT = 3

TARGET_RATIO = 3.2

TIMEOUT = 3  # seconds
RESULT_TIMEOUT = 2  # seconds
WIN_RESULT_TIMEOUT = 30  # seconds


# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class GearRatio (threading.Thread, queue_common.QueueCommon):
    STATE_QUIT = -1

    def __init__(self):
        self._ratio_count = 0
        self._last_event_time = None
        self._last_result_time = None
        self._state = 0
        self._rotations = 0
        self._timeout = RESULT_TIMEOUT
        GPIO.add_event_detect(pins.ENC0, GPIO.FALLING, callback=self.on_enc0, bouncetime=30)
        GPIO.add_event_detect(pins.ENC1, GPIO.FALLING, callback=self.on_enc1, bouncetime=30)
        threading.Thread.__init__(self)
        queue_common.QueueCommon.__init__(self)

    def on_enc0(self, pin):
        if self._last_event_time is None or time.time() - self._last_event_time > TIMEOUT:
            self._ratio_count = 0
            self._rotations = 0
            self.send_event(event.Event(event.SOURCE_GEARS, event.EVENT_PLAY_SOUND, RESULT_TOO_LOW))
        else:
            print("Finished a full rotation, count was " + str(self._ratio_count))
            if self._rotations < 10:
                self._last_event_time = time.time()
                self._rotations += 1
                return
            self._rotations = 0
            ratio = self._ratio_count / 10.0
            self._ratio_count = 0
            print("10 clicks, ratio was " + str(ratio))
            # Don't send a new result too frequently
            if self._last_result_time is not None and time.time() - self._last_result_time < self._timeout:
                self._last_event_time = time.time()
                return
            elif 2.6 < ratio < 3.25:
                self.send_event(event.Event(event.SOURCE_GEARS, event.EVENT_PLAY_SOUND, RESULT_JUST_RIGHT))
                self._timeout = WIN_RESULT_TIMEOUT
            elif ratio <= 2.6:
                self.send_event(event.Event(event.SOURCE_GEARS, event.EVENT_PLAY_SOUND, RESULT_TOO_LOW))
                self._timeout = RESULT_TIMEOUT
            else:
                self.send_event(event.Event(event.SOURCE_GEARS, event.EVENT_PLAY_SOUND, RESULT_TOO_HIGH))
                self._timeout = RESULT_TIMEOUT
            self._last_result_time = time.time()
        self._last_event_time = time.time()

    def on_enc1(self, pin):
        self._ratio_count += 1
        if self._last_event_time is None:
            self.send_event(event.Event(event.SOURCE_GEARS, event.EVENT_PLAY_SOUND, RESULT_TOO_LOW))
        self._last_event_time = time.time()

    def handle_command(self, command):
        if command.command == COMMAND_QUIT:
            self._state = self.STATE_QUIT

    def run(self):
        print("Running gear ratios!")
        while True:
            if self._state == self.STATE_QUIT:
                break
            self.check_queue()
            time.sleep(0.1)
            if self._last_event_time is not None and time.time() - self._last_event_time > TIMEOUT:
                self.send_event(event.Event(event.SOURCE_GEARS, event.EVENT_PLAY_SOUND))
                self._last_event_time = None
                self._timeout = RESULT_TIMEOUT
                self._rotations = 0

        GPIO.remove_event_detect(pins.ENC0)
        GPIO.remove_event_detect(pins.ENC1)
        return
