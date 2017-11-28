import threading


# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class GearRatio (threading.Thread):
    PIN1 = 5
    PIN2 = 6

    STATE_QUIT = -1
    STATE_IDLE = 1
    STATE_START = 2
    STATE_COUNTING = 3
    STATE_RESULT = 4

    RESULT_SOUNDS = [] #TODO add filenames for different result sounds

    def __init__(self):
        self._state = self.STATE_IDLE
        self._result = 0
        threading.Thread.__init__(self)

    def wait_for_first_click(self):
        #TODO wait for PIN1 to change then we'll start the music
        self._state = self.STATE_START
        return

    def wait_for_second_click(self):
        #TODO wait for PIN2 to change, then we'll start counting revolutions
        #TODO if timer expires reset
        self._state = self.STATE_COUNTING

    def count_clicks(self):
        #TODO count the ratio of PIN2 to PIN1 to check if the ratio is correct.
        self._result = 4 #set to ratio
        self._state = self.STATE_RESULT

    def play_result(self):
        #TODO play the sound file that is closest to the result
        self._state = self.STATE_QUIT

    def error(self):
        print("Unknown error in gear ratios!")

    def state_to_strings(self):
        switcher = {
            self.STATE_IDLE: self.wait_for_first_click,
            self.STATE_START: self.wait_for_second_click,
            self.STATE_COUNTING: self.count_clicks,
            self.STATE_RESULT: self.play_result
        }
        return switcher.get(self._state, self.error)

    def run(self):
        print("Running gear ratios!")
        while True:
            if self._state == self.STATE_QUIT:
                break
            print("Entering state " + str(self._state))
            f_state = self.state_to_strings()
            f_state()
        #TODO switch statement for state changes
        return
