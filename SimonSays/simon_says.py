import random
import threading
import time

# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class SimonSays (threading.Thread):
    BUTTONS = ["(R)ed", "(B)lue", "(G)reen", "(Y)ellow"]
    BUTTON_LETTER = ["R", "B", "G", "Y"]
    LIT_TIME = .7
    OFF_TIME = .25

    def waitForPress(self):
        value = getChar()
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


def getChar():
    # figure out which function to use once, and store it in _func
    if "_func" not in getChar.__dict__:
        try:
            # for Windows-based systems
            import msvcrt # If successful, we are on Windows
            print("On Windows hit enter after every key")
            # getch doesn't work in IDEs, if on the cmd line can use msvcrt.getch
            getChar._func = input

        except ImportError:
            # for POSIX-based systems (with termios & tty support)
            import tty, sys, termios # raises ImportError if unsupported

            def _ttyRead():
                fd = sys.stdin.fileno()
                oldSettings = termios.tcgetattr(fd)

                try:
                    tty.setraw(fd)
                    answer = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

                return answer

            getChar._func = _ttyRead

    return getChar._func()

simonThread = SimonSays()
simonThread.start()
