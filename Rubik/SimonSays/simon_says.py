import random
import threading
import time
import RPi.GPIO as GPIO

from .. import utils
from .. import event
from .. import queue_common
from .. import pins

Command = queue_common.Command

MODE_LISTENING = 0
MODE_PLAYING = 1

COMMAND_QUIT = -1
COMMAND_CHANGE_MODE = 0


# Sounds note: Could use http://simpleaudio.readthedocs.io/en/latest/installation.html
class SimonSays(threading.Thread, queue_common.QueueCommon):
    BUTTON_STRINGS = ["(R)ed", "(B)lue", "(G)reen", "(Y)ellow", "(W)hite"]
    BUTTON_LETTERS = ["R", "B", "G", "Y", "W"]
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

    # GPIO.input(pin)
    # channel = GPIO.wait_for_edge(channel, GPIO_RISING, timeout=5000)
    # GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback)
    BUTTON_PINS = [
        pins.SW4_IN,
        pins.SW3_IN,
        pins.SW2_IN,
        pins.SW1_IN,
        pins.SW0_IN
    ]
    # GPIO.output(pin, GPIO.LOW or GPIO.HIGH)
    LED_PINS = [
        pins.SW4_LED,
        pins.SW3_LED,
        pins.SW2_LED,
        pins.SW1_LED,
        pins.SW0_LED,
    ]
    BUTTON_LETTER_TO_PIN = {
        "Y": BUTTON_PINS[0],
        "G": BUTTON_PINS[1],
        "W": BUTTON_PINS[2],
        "R": BUTTON_PINS[3],
        "B": BUTTON_PINS[4],
    }
    PIN_TO_LETTER = {
        BUTTON_PINS[0]: "Y",
        BUTTON_PINS[1]: "G",
        BUTTON_PINS[2]: "W",
        BUTTON_PINS[3]: "R",
        BUTTON_PINS[4]: "B"
    }
    BUTTON_LETTER_TO_LED = {
        "Y": LED_PINS[0],
        "G": LED_PINS[1],
        "W": LED_PINS[2],
        "R": LED_PINS[3],
        "B": LED_PINS[4],
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
        self._is_listening = False
        self._button_queue = []
        threading.Thread.__init__(self)
        queue_common.QueueCommon.__init__(self)
        self.start_listening_for_events()

    def start_listening_for_events(self):
        if self._is_listening:
            return
        print("Started listening for button events")
        GPIO.add_event_detect(self.BUTTON_PINS[0], GPIO.FALLING, callback=self.on_press_b1, bouncetime=150)
        GPIO.add_event_detect(self.BUTTON_PINS[1], GPIO.FALLING, callback=self.on_press_b2, bouncetime=150)
        GPIO.add_event_detect(self.BUTTON_PINS[2], GPIO.FALLING, callback=self.on_press_b3, bouncetime=150)
        GPIO.add_event_detect(self.BUTTON_PINS[3], GPIO.FALLING, callback=self.on_press_b4, bouncetime=150)
        GPIO.add_event_detect(self.BUTTON_PINS[4], GPIO.FALLING, callback=self.on_press_b5, bouncetime=150)
        self._is_listening = True

    def stop_listening_for_events(self):
        if not self._is_listening:
            return

        print("Stopped listening for button events")
        GPIO.remove_event_detect(self.BUTTON_PINS[0])
        GPIO.remove_event_detect(self.BUTTON_PINS[1])
        GPIO.remove_event_detect(self.BUTTON_PINS[2])
        GPIO.remove_event_detect(self.BUTTON_PINS[3])
        GPIO.remove_event_detect(self.BUTTON_PINS[4])
        self._is_listening = False

    def on_press_b1(self, button):
        if self._mode == MODE_LISTENING:
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_BUTTON1))
        else:
            self._button_queue.append(self.PIN_TO_LETTER[self.BUTTON_PINS[0]])
        print("b1 pressed")

    def on_press_b2(self, button):
        if self._mode == MODE_LISTENING:
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_BUTTON2))
        else:
            self._button_queue.append(self.PIN_TO_LETTER[self.BUTTON_PINS[1]])
        print("b2 pressed")

    def on_press_b3(self, button):
        if self._mode == MODE_LISTENING:
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_BUTTON3))
        else:
            self._button_queue.append(self.PIN_TO_LETTER[self.BUTTON_PINS[2]])
        print("b3 pressed")

    def on_press_b4(self, button):
        if self._mode == MODE_LISTENING:
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_BUTTON4))
        else:
            self._button_queue.append(self.PIN_TO_LETTER[self.BUTTON_PINS[3]])
        print("b4 pressed")

    def on_press_b5(self, button):
        if self._mode == MODE_LISTENING:
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_BUTTON5))
        else:
            self._button_queue.append(self.PIN_TO_LETTER[self.BUTTON_PINS[4]])
        print("b5 pressed")

    def wait_for_press(self, timeout):
        # Wait for correct button or timeout
        start_time = time.time()
        if utils.use_buttons():
            # pin = GPIO.wait_for_edge(self.BUTTON_PINS[index], GPIO.FALLING,
            #                          timeout=int(self._curr_speed * self.TIMEOUT * 1000))
            # GPIO.remove_event_detect(self.BUTTON_PINS[index])
            # if pin is None:
            #     return 'Z'
            # return self.PIN_TO_LETTER[pin]
            while len(self._button_queue) == 0:
                if time.time() - start_time > timeout:
                    return 'Z'
                time.sleep(.02)
            return self._button_queue.pop(0)
        else:
            return utils.get_char()

    def show_value(self, value):
        pin = self.BUTTON_LETTER_TO_LED[value]
        GPIO.output(pin, GPIO.HIGH)
        print("\r" + value)  # , sep=' ', end='', flush=True)

    def turn_off(self, value):
        for pin in self.LED_PINS:
            GPIO.output(pin, GPIO.LOW)
        clear = " " * len(value)
        print("\r" + clear)  # , sep=' ', end='', flush=True)
        return

    def add_random(self, seq):
        index = random.randint(0, len(self.BUTTON_STRINGS) - 1)
        # print("rand value was " + str(index))
        seq.append(index)

    def play_sequence(self, seq):
        print("Watch close")
        for val in seq:
            time.sleep(self.OFF_TIME * self._curr_speed)
            colorStr = self.BUTTON_LETTERS[val]
            self.show_value(colorStr)
            self.send_event(event.Event(event.SOURCE_SIMON,
                                        event.EVENT_PLAY_SOUND,
                                        self.BUTTON_EVENTS[val],
                                        self._curr_speed))
            time.sleep(self.LIT_TIME * self._curr_speed)
            self.turn_off(colorStr)
        print("\nNow repeat")

    def read_sequence(self, seq):
        self._button_queue = []
        for index in seq:
            wait_start = time.time()
            val = self.wait_for_press(self.TIMEOUT * self._curr_speed)
            delay = time.time() - wait_start
            if delay > self.TIMEOUT * self._curr_speed:
                print("Too slow!")
                return False
            if val.upper() != self.BUTTON_LETTERS[index]:
                print("You lose! expected " + self.BUTTON_LETTERS[index] + " but got " + val)
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
            # self.stop_listening_for_events()
            self._mode = command.data
            # if self._mode == MODE_LISTENING:
            #     self.start_listening_for_events()

    def run(self):
        GPIO.output((pins.SW0_LED, pins.SW1_LED, pins.SW2_LED, pins.SW3_LED, pins.SW4_LED), GPIO.HIGH)
        time.sleep(1)
        GPIO.output((pins.SW0_LED, pins.SW1_LED, pins.SW2_LED, pins.SW3_LED, pins.SW4_LED), GPIO.LOW)
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
