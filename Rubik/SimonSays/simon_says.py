import random
import threading
import time
from .. import utils

# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class SimonSays (threading.Thread):

    BUTTONS = ["(R)ed", "(B)lue", "(G)reen", "(Y)ellow"]
    BUTTON_LETTER = ["R", "B", "G", "Y"]
    LIT_TIME = .7
    OFF_TIME = .25

    def waitForPress(self):
        value = utils.getChar() #getChar()
        return value

    def showValue(self, value):
        # TODO: turn on correct button & play sound
        print("\r" + value, sep=' ', end='', flush=True)

    def turnOff(self, value):
        # TODO: stop showing all values/sounds
        clear = " " * len(value)
        print("\r" + clear, sep=' ', end='', flush=True)
        return

    def addRandom(self, seq):
        index = random.randint(0, len(self.BUTTONS) - 1)
        #print("rand value was " + str(index))
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

    def run(self):
        sequence = []
        while True:
            self.addRandom(sequence)
            self.playSequence(sequence)
            if not self.readSequence(sequence):
                break

