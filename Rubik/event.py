class Event:
    def __init__(self, source, event, data=None):
        self.source = source
        self.event = event
        self.data = data


SOURCE_OTHER = 0
SOURCE_GUI = 1
SOURCE_RUBIK = 2
SOURCE_SIMON = 3
SOURCE_GEARS = 4

EVENT_DEFAULT = 0
EVENT_BUTTON1 = 1
EVENT_BUTTON2 = 2
EVENT_BUTTON3 = 3
EVENT_BUTTON4 = 4
EVENT_BUTTON5 = 5
EVENT_CUBE_LIFT = 6
EVENT_CUBE_SET = 7
EVENT_SUCCESS = 8
EVENT_FAILURE = 9
EVENT_BUTTON_RESET = -1

EVENT_STRINGS = {
    EVENT_DEFAULT: "DEFAULT",
    EVENT_BUTTON1: "BUTTON1",
    EVENT_BUTTON2: "BUTTON2",
    EVENT_BUTTON3: "BUTTON3",
    EVENT_BUTTON4: "BUTTON4",
    EVENT_BUTTON5: "BUTTON5",
    EVENT_CUBE_LIFT: "CUBE LIFT",
    EVENT_CUBE_SET: "CUBE SET",
    EVENT_SUCCESS: "SUCCESS",
    EVENT_FAILURE: "FAILURE",
    EVENT_BUTTON_RESET: "RESET"
}