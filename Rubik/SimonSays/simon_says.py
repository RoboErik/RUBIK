import random
import threading
import time
import RPi.GPIO as GPIO

from Queue import *
from .. import utils
from .. import event

MODE_LISTENING = 0
MODE_PLAYING = 1

COMMAND_QUIT = -1
COMMAND_CHANGE_MODE = 0


class Command:
    command = None
    data = None

    def __init__(self, command, data=None):
        self.command = command
        self.data = data


# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class SimonSays(threading.Thread):
    BUTTONS = ["(R)ed", "(B)lue", "(G)reen", "(Y)ellow"]
    BUTTON_LETTER = ["R", "B", "G", "Y"]
    LIT_TIME = .7
    OFF_TIME = .25

    _mode = MODE_LISTENING
    _command_queue = Queue()
    _event_queue = None
    _score = 0

    def on_press_b1(self):
        print("b1 pressed")

    def waitForPress(self):
        value = utils.getChar()  # getChar()
        return value

    def showValue(self, value):
        # TODO: turn on correct button & play sound
        print("\r" + value)  # , sep=' ', end='', flush=True)

    def turnOff(self, value):
        # TODO: stop showing all values/sounds
        clear = " " * len(value)
        print("\r" + clear)  # , sep=' ', end='', flush=True)
        return

    def addRandom(self, seq):
        index = random.randint(0, len(self.BUTTONS) - 1)
        # print("rand value was " + str(index))
        seq.append(index)

    def playSequence(self, seq):
        print("Watch close")
        for val in seq:
            time.sleep(self.OFF_TIME)
            colorStr = self.BUTTONS[val]
            self.showValue(colorStr)
            time.sleep(self.LIT_TIME)
            self.turnOff(colorStr)
        print("\nNow repeat")

    def readSequence(self, seq):
        for index in seq:
            val = self.waitForPress()
            if val.upper() != self.BUTTON_LETTER[index]:
                print("You lose!")
                return False
        print("\nWell done")
        return True

    def get_queue(self):
        return self._command_queue

    def set_event_queue(self, queue):
        self._event_queue = queue

    def check_queue(self):
        try:
            command = self._command_queue.get(False)
            print("Received command in Simon Says: " + str(command))
            if command.command == COMMAND_QUIT:
                self._mode = -1
            elif command.command == COMMAND_CHANGE_MODE:
                self._mode = command.data
            self._command_queue.task_done()
        except Empty:
            pass

    def run(self):
        # TODO finalize pin ports
        GPIO.add_event_detect(17, GPIO.FALLING, callback=self.on_press_b1, bouncetime=300)
        while self._mode != -1:
            if self._mode == MODE_PLAYING:
                print("Starting Simon Says!")
                sequence = []
                score = 0
                while self._mode == MODE_PLAYING:
                    self.addRandom(sequence)
                    self.playSequence(sequence)
                    if not self.readSequence(sequence):
                        if self._event_queue is not None:
                            self._event_queue.put(event.Event(event.SOURCE_SIMON,
                                                              event.EVENT_FAILURE,
                                                              score))
                            self._mode = MODE_LISTENING
                        break
                    score += 1
                    self.check_queue()
            elif self._mode == MODE_LISTENING:
                # TODO listen for button presses and send them to controller
                self.check_queue()
                time.sleep(0.1)
        GPIO.remove_event_detect(17)
