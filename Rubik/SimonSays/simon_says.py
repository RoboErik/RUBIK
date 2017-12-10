import random
import threading
import time
import RPi.GPIO as GPIO

from .. import utils
from .. import event
from .. import queue_common

Command = queue_common.Command

MODE_LISTENING = 0
MODE_PLAYING = 1

COMMAND_QUIT = -1
COMMAND_CHANGE_MODE = 0


# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class SimonSays(threading.Thread, queue_common.QueueCommon):
    BUTTONS = ["(R)ed", "(B)lue", "(G)reen", "(Y)ellow", "(W)hite"]
    BUTTON_LETTER = ["R", "B", "G", "Y", "W"]
    BUTTON_EVENTS = [event.EVENT_BUTTON4,  # R
                     event.EVENT_BUTTON5,  # B
                     event.EVENT_BUTTON2,  # G
                     event.EVENT_BUTTON1,  # Y
                     event.EVENT_BUTTON3]  # W
    BUTTON_LETTER_TO_EVENT = {
        "Y": event.EVENT_BUTTON1,
        "G": event.EVENT_BUTTON2,
        "W": event.EVENT_BUTTON3,
        "R": event.EVENT_BUTTON4,
        "B": event.EVENT_BUTTON5,
    }
    LIT_TIME = .75
    OFF_TIME = .25
    SPEED_SCALE = 0.98
    MIN_SPEED = 0.4
    TIMEOUT = 2.5

    def __init__(self):
        self._mode = MODE_LISTENING
        self._score = 0
        self._curr_speed = 1
        threading.Thread.__init__(self)
        queue_common.QueueCommon.__init__(self)

    def on_press_b1(self):
        if self._mode == MODE_LISTENING:
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_BUTTON1))
        print("b1 pressed")

    def wait_for_press(self):
        # TODO wait for correct button or timeout
        value = utils.getChar()
        return value

    def show_value(self, value):
        # TODO: turn on correct button & play sound
        print("\r" + value)  # , sep=' ', end='', flush=True)

    def turn_off(self, value):
        # TODO: stop showing all values/sounds
        clear = " " * len(value)
        print("\r" + clear)  # , sep=' ', end='', flush=True)
        return

    def add_random(self, seq):
        index = random.randint(0, len(self.BUTTONS) - 1)
        # print("rand value was " + str(index))
        seq.append(index)

    def play_sequence(self, seq):
        print("Watch close")
        for val in seq:
            time.sleep(self.OFF_TIME * self._curr_speed)
            colorStr = self.BUTTONS[val]
            self.show_value(colorStr)
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_PLAY_SOUND,
                                        self.BUTTON_EVENTS[val],
                                        self._curr_speed))
            time.sleep(self.LIT_TIME * self._curr_speed)
            self.turn_off(colorStr)
        print("\nNow repeat")

    def read_sequence(self, seq):
        for index in seq:
            wait_start = time.time()
            val = self.wait_for_press()
            delay = time.time() - wait_start
            if delay > self.TIMEOUT * self._curr_speed:
                print("Too slow!")
                return False
            if val.upper() != self.BUTTON_LETTER[index]:
                print("You lose!")
                return False
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_PLAY_SOUND,
                                        self.BUTTON_LETTER_TO_EVENT[val.upper()]))
        print("\nWell done")
        return True

    def handle_command(self, command):
        print("Received command in Simon Says: " + str(command))
        if command.command == COMMAND_QUIT:
            self._mode = -1
        elif command.command == COMMAND_CHANGE_MODE:
            self._mode = command.data

    def run(self):
        # TODO finalize pin ports
        GPIO.add_event_detect(17, GPIO.FALLING, callback=self.on_press_b1, bouncetime=300)
        while self._mode != -1:
            if self._mode == MODE_PLAYING:
                print("Starting Simon Says!")
                sequence = []
                score = 0
                self._curr_speed = 1.0
                while self._mode == MODE_PLAYING:
                    self.add_random(sequence)
                    self.play_sequence(sequence)
                    self.send_event(event.Event(event.SOURCE_SIMON,
                                                event.EVENT_UPDATE,
                                                score,
                                                self._curr_speed))
                    if not self.read_sequence(sequence):
                        self.send_event(event.Event(event.SOURCE_SIMON,
                                                    event.EVENT_FAILURE,
                                                    score))
                        self._mode = MODE_LISTENING
                        break
                    score += 1
                    self._curr_speed *= self.SPEED_SCALE
                    if self._curr_speed < self.MIN_SPEED:
                        self._curr_speed = self.MIN_SPEED

                    self.send_event(event.Event(event.SOURCE_SIMON,
                                                event.EVENT_UPDATE,
                                                score))
                    self.check_queue()
                    time.sleep(1)
            elif self._mode == MODE_LISTENING:
                # TODO listen for button presses and send them to controller
                self.check_queue()
                time.sleep(0.1)
        GPIO.remove_event_detect(17)
