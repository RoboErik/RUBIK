import threading

# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class GearRatio (threading.Thread):
    PIN1 = 5
    PIN2 = 6

    STATE_IDLE = 1
    STATE_START = 2
    STATE_COUNTING = 3
    STATE_RESULT = 4

    RESULT_SOUNDS = [] #TODO add filenames for different result sounds

    mState = STATE_IDLE
    mResult = 0

    def waitForFirstClick(self):
        #TODO wait for PIN1 to change then we'll start the music
        self.mState = self.STATE_START
        return

    def waitForSecondClick(self):
        #TODO wait for PIN2 to change, then we'll start counting revolutions
        #TODO if timer expires reset
        self.mState = self.STATE_COUNTING

    def countClicks(self):
        #TODO count the ratio of PIN2 to PIN1 to check if the ratio is correct.
        self.mResult = 4 #set to ratio

    def playResult(self):
        #TODO play the sound file that is closest to the result
        return

    def run(self):
        print("Running gear ratios!")
        #TODO switch statement for state changes
        return
