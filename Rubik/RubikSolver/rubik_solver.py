import threading
import RPi.GPIO as GPIO
import time
import random
import math
from . import switch_timer
from .. import utils
from .. import pins
from .. import queue_common
from .. import event

# For reading the color sensors
from color_sensors import ColorSensors
from leds import LedStrip
from sensor_targets import *

from .rpi_ws281x.python.neopixel import *

Command = queue_common.Command

COMMAND_SET_MODE = 1

MODE_QUIT = -1
# In this mode don't do anything
MODE_IDLE = 0
# In this mode just records the time between lifting and replacing the Cube.
MODE_TIME = 1
# In this mode generates a pattern and checks for that pattern on down.
MODE_PATTERN = 2
# In this mode use the test interface
MODE_TEST = 3

CLEAR_INDEX = 0
RED_INDEX = 1
GREEN_INDEX = 2
BLUE_INDEX = 3

RED = 0xaa0000
GREEN = 0x00aa00
BLUE = 0x0000aa
YELLOW = 0xcccc00
ORANGE = 0xbb4000
WHITE = 0xaaaaaa

LED_COLORS = [RED, GREEN, BLUE, YELLOW, ORANGE, WHITE]
LED_CODES = ['R', 'G', 'B', 'Y', 'O', 'W']
TEST_PATTERN = ['W', 'G', 'B', 'Y', 'O', 'R', 'G', 'B', 'G']
TEST_PATTERN2 = ['W', 'W', 'W', 'B', 'B', 'G', 'B', 'B', 'B']
ALL_RED = ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']
LED_PATTERN_BRIGHTNESS = 20

# The LEDs and the color sensors are transposes of each other, so this
# mapping works both ways.
DISPLAY_TO_READ_INDEX = [0, 3, 6, 1, 4, 7, 2, 5, 8]

LED_SENSOR_COLOR = Color(255, 235, 130)
LED_SENSOR_BRIGHTNESS = 15

# How long to flash each color to indicate the solve timer is going.
TIMER_BLINK_TIME = 0.5
# Time to show the pattern to solve for in seconds.
PATTERN_DISPLAY_TIME = 5.0
# Timeout for cancelling the game if not won yet in seconds.
RUNNING_TIMEOUT = 30 * 60
# The max attempts before the game is lost.
MAX_ATTEMPTS = 2

# All the target arrays in one big array
COLOR_TARGETS = COLOR_TARGETS_15

STATE_NOT_RUNNING = 0
STATE_WAITING_TO_START = 1
STATE_DISPLAYING_PATTERN = 2
STATE_WAITING_WRONG_PATTERN = 3
STATE_TIMING = 4
STATE_CUBE_NOT_DOWN = 5


# Does not solve a Rubik cube, but either times how long it took to solve or
# requires a specific pattern be created.
class RubikSolver(threading.Thread, queue_common.QueueCommon):

    def __init__(self):
        self. _state = STATE_NOT_RUNNING
        self._mode = MODE_IDLE
        self._source = event.SOURCE_MATCH
        self._pattern = []
        self._result = []
        self._attempts = 0

        self._start_time = 0
        self._pattern_shown_time = 0;
        self._timer = switch_timer.SwitchTimer()
        self._stop_event = threading.Event()
        self._color_sensors = None
        self._led_strip = None
        self._waiting_led_on = False
        self._blink_color = None
        threading.Thread.__init__(self)
        queue_common.QueueCommon.__init__(self)

    def handle_command(self, command):
        if command.command == COMMAND_SET_MODE:
            new_mode = command.data
            self.set_mode(new_mode)

    def set_mode(self, mode):
            if mode != self._mode:
                self.hide_pattern()
                self._state = STATE_NOT_RUNNING
                self._mode = mode
                if self._mode == MODE_TIME:
                    self._source = event.SOURCE_TIMER
                else:
                    self._source = event.SOURCE_MATCH

    def generate_pattern(self):
        if True:
            self._pattern = TEST_PATTERN2
            return
        self._pattern = []
        for i in range(9):
            self._pattern.append(LED_CODES[random.randint(0, 5)])

    def show_pattern(self, pattern):
        self._led_strip.set_brightness(LED_PATTERN_BRIGHTNESS)
        for i in range(len(pattern)):
            self._led_strip.set_led(i, LED_COLORS[LED_CODES.index(pattern[i])])

    def hide_pattern(self):
        self._led_strip.set_brightness(0)
        self._led_strip.set_all_leds(0)

    def set_led(self, led, color):
        self._led_strip.set_brightness(LED_PATTERN_BRIGHTNESS)
        self._led_strip.set_led(led, color)

    def set_all_leds(self, color):
        self._led_strip.set_brightness(LED_PATTERN_BRIGHTNESS)
        self._led_strip.set_all_leds(color)

    def is_all_same(self):
        color_codes = self.read_colors()
        color = color_codes[0]
        for i in range(1, len(color_codes)):
            if color_codes[i] != color:
                return False
        return True

    def is_pattern_correct(self):
        color_codes = self.read_colors()
        print("Checking colors: expected " + str(self._pattern) + ", actual " + str(color_codes))
        for i in range(len(color_codes)):
            if color_codes[i] != self._pattern[DISPLAY_TO_READ_INDEX[i]]:
                return False
        return True

    def read_colors(self):
        self._led_strip.set_brightness(LED_SENSOR_BRIGHTNESS)
        self._led_strip.set_all_leds(LED_SENSOR_COLOR)
        time.sleep(0.1)
        results = []
        for i in range(9):
            guess_index = guess_color(i, self._read_color(i))
            if guess_index >= 0:
                results.append(LED_CODES[guess_index])
            else:
                results.append('F')
        self.hide_pattern()
        time.sleep(0.1)
        return results

    def cube_is_down(self):
        colors = self._read_color(4)
        if colors[CLEAR_INDEX] <= 5:
            return True
        return False

    def check_timeout(self):
        if self._state != STATE_NOT_RUNNING:
            if time.time() - self._start_time > RUNNING_TIMEOUT:
                self._state = STATE_NOT_RUNNING
                self._mode = MODE_IDLE
                self.send_event(event.Event(self._source, event.EVENT_FAILURE, 3599.99))

    def update_solver_state(self):
        # Timeout protection
        self.check_timeout()
        if self._state == STATE_NOT_RUNNING:
            self._start_time = time.time()
            if self.cube_is_down():
                self._state = STATE_WAITING_TO_START
            else:
                self._state = STATE_CUBE_NOT_DOWN
            return
        if self._state == STATE_CUBE_NOT_DOWN:
            blink_count = int(math.floor((time.time() - self._start_time) / TIMER_BLINK_TIME))
            turn_on_wait = (blink_count % 2) == 1
            if turn_on_wait != self._waiting_led_on:
                if turn_on_wait:
                    self.set_led(4, 0xbbbbbb)
                else:
                    self.hide_pattern()
                self._waiting_led_on = turn_on_wait
            elif not turn_on_wait:
                if self.cube_is_down():
                    self._state = STATE_WAITING_TO_START
            return
        if self._state == STATE_WAITING_TO_START:
            if not self.cube_is_down():
                self._start_time = time.time()
                self._state = STATE_DISPLAYING_PATTERN
            return
        if self._state == STATE_DISPLAYING_PATTERN:
            curr_time = self._update_time()
            color_index = int(math.floor(curr_time / TIMER_BLINK_TIME))
            if color_index < len(LED_COLORS):
                self.set_all_leds(LED_COLORS[color_index])
            else:
                self.hide_pattern()
                self._state = STATE_TIMING
            return
        if self._state == STATE_TIMING:
            curr_time = self._update_time()
            if self.cube_is_down() and self.is_all_same():
                self._state = STATE_NOT_RUNNING
                self.send_event(event.Event(self._source, event.EVENT_SUCCESS, curr_time))
                self.set_mode(MODE_IDLE)
            return

    # While in the pattern matching game that state machine looks like this:
    # 1. Not running
    # 2. Waiting for the cube to be picked up
    # 3. Showing the pattern
    # 4. Waiting for the cube to be put down again
    # 5. Checking the pattern, if wrong go back to 3 on pick up.
    # 6. If correct, send the winning time and go back to idle mode.
    def update_pattern_state(self):
        # Timeout protection
        self.check_timeout()
        if self._state == STATE_NOT_RUNNING:
            self.generate_pattern()
            self._attempts = 0
            # This isn't the actual start time but is used for the timeout
            self._start_time = time.time()
            self._state = STATE_WAITING_TO_START
            return
        if self._state == STATE_WAITING_TO_START:
            if not self.cube_is_down():
                self.show_pattern(self._pattern)
                self._start_time = time.time()
                self._pattern_shown_time = self._start_time
                self._state = STATE_DISPLAYING_PATTERN
            return
        if self._state == STATE_DISPLAYING_PATTERN:
            self._update_time()
            if (time.time() - self._pattern_shown_time) > 5:
                self.hide_pattern()
                self._state = STATE_TIMING
            return
        if self._state == STATE_TIMING:
            curr_time = self._update_time()
            if self.cube_is_down():
                if self.is_pattern_correct():
                    self._state = STATE_NOT_RUNNING
                    self.send_event(event.Event(self._source, event.EVENT_SUCCESS, curr_time))
                    self.set_mode(MODE_IDLE)
                else:
                    self._attempts += 1
                    if self._attempts >= MAX_ATTEMPTS:
                        self._state = STATE_NOT_RUNNING
                        self.send_event(event.Event(self._source, event.EVENT_FAILURE, curr_time))
                        self.set_mode(MODE_IDLE)
                    else:
                        self._state = STATE_WAITING_WRONG_PATTERN
            return
        if self._state == STATE_WAITING_WRONG_PATTERN:
            self._update_time()
            if not self.cube_is_down():
                self.show_pattern(self._pattern)
                self._state = STATE_DISPLAYING_PATTERN
                self._pattern_shown_time = time.time()

    # Sends the current playtime as an event and returns the playtime.
    def _update_time(self):
        curr_time = time.time() - self._start_time
        self.send_event(event.Event(self._source, event.EVENT_UPDATE, curr_time))
        return curr_time

    def _read_color(self, index):
        self._color_sensors.set_sensor(index)
        colors = self._color_sensors.getColors()
        return colors

    def _setup(self):
        print("Setup of RubikSolver")
        self._color_sensors = ColorSensors()
        self._led_strip = LedStrip()

    def _teardown(self):
        print("Teardown of RubikSolver")
        GPIO.remove_event_detect(pins.RUBIK_CUBE_SWITCH)

        self._color_sensors.clear_active()
        self.hide_pattern()

        # Is this cleanup necessary?
        del self._led_strip
        self._led_strip = None
        del self._color_sensors
        self._color_sensors = None


    def stop(self):
        print("Stopping RubikSolver! Time is " + str(utils.curr_time_s()))
        self._stop_event.set()

    def run(self):
        self._setup()

        while self._mode != MODE_QUIT:
            if self._mode == MODE_TEST:
                print("test (p)attern, (g)uessing, or (c)ollect data? (q)uit")
                value = utils.getChar()
                if value == 'p':
                    self.test_pattern_display()
                elif value == 'c':
                    csv = open("csv_colors.txt", 'w')
                    self.collect_color_data(csv)
                    csv.close()
                elif value == 'g':
                    self.test_guessing()
                elif value == 'q':
                    self._mode = MODE_QUIT
            elif self._mode == MODE_IDLE:
                time.sleep(0.1)
            elif self._mode == MODE_PATTERN:
                self.update_pattern_state()
                time.sleep(0.05)
            elif self._mode == MODE_TIME:
                self.update_solver_state()
                time.sleep(0.05)
            self.check_queue()

        self._teardown()

    def test_pattern_display(self):
        pattern = TEST_PATTERN
        self.show_pattern(pattern)
        utils.getChar()
        self.hide_pattern()
        self.generate_pattern()
        self.show_pattern(pattern)
        utils.getChar()
        self.hide_pattern()

    def test_guessing(self):
        while True:
            print("Check colors? Y/N")
            value = utils.getChar()
            if value.upper() != 'Y':
                return
            print("Colors: " + str(self.read_colors()))

    def collect_color_data(self, csv):
        print("Ready to collect color data. Press r to retry or any other key to continue.")
        value = 'r'
        while value == 'r':
            self._led_strip.set_brightness(0)
            time.sleep(.2)
            self._led_strip.set_brightness(LED_SENSOR_BRIGHTNESS)
            self._led_strip.set_all_leds(LED_SENSOR_COLOR)
            value = utils.getChar()

        sums = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        samples = 11
        incr_brightness = False
        brightness = -5 if incr_brightness else LED_SENSOR_BRIGHTNESS
        csv.write("Sensor, Red/Green ratio, Red/Blue ratio, Green/Blue ratio, sample\n")
        for i in range(9 * samples):
            sensor = i % 9
            if sensor is 0:
                print("\nSAMPLE " + str(i / 9) + ":\n")
                if incr_brightness:
                    brightness += 10
                    self._led_strip.set_brightness(brightness)
            # self.color_sensors.set_sensor(sensor)
            # colors = self.color_sensors.getColors()
            colors = self._read_color(sensor)
            red_green_ratio = colors[RED_INDEX] / float(colors[GREEN_INDEX])
            red_blue_ratio = colors[RED_INDEX] / float(colors[BLUE_INDEX])
            green_blue_ratio = colors[GREEN_INDEX] / float(colors[BLUE_INDEX])
            sums[sensor][0] += red_green_ratio
            sums[sensor][1] += red_blue_ratio
            sums[sensor][2] += green_blue_ratio

            guess = get_color_ratio_string(colors)
            csv.write(str(sensor) + ", " + guess + ", " + str(i) + "\n")
            print(str(sensor) + ": " + guess + " at Brightness=" + str(brightness))
            time.sleep(.1)
        print("\n\nAverages:\n")
        for i in range(9):
            print("Sensor " + str(i) + ": r/g=" + str(sums[i][0] / samples)
                  + ", r/b=" + str(sums[i][1] / samples)
                  + ", g/b=" + str(sums[i][2] / samples) + "\n")

        print("\n[")
        for i in range(9):
            print("[" + str(round(sums[i][0] / samples, 3))
                  + ", " + str(round(sums[i][1] / samples, 3))
                  + ", " + str(round(sums[i][2] / samples, 3)) + "],  # sensor " + str(i))
        print("]")


def get_color_ratio_string(colors):
    if colors[CLEAR_INDEX] < 1 or colors[GREEN_INDEX] < 1 or colors[BLUE_INDEX] < 1:
        return "none, none, none"

    red_green_ratio = colors[RED_INDEX] / float(colors[GREEN_INDEX])
    red_blue_ratio = colors[RED_INDEX] / float(colors[BLUE_INDEX])
    green_blue_ratio = colors[GREEN_INDEX] / float(colors[BLUE_INDEX])
    ratio_string = str(red_green_ratio) + ", " + str(red_blue_ratio) + ", " + str(green_blue_ratio)

    return ratio_string


def guess_color(sensor, colors):
    if colors[GREEN_INDEX] < 1 or colors[BLUE_INDEX] < 1:
        return -1  # Too dark

    red_green_ratio = colors[RED_INDEX] / float(colors[GREEN_INDEX])
    red_blue_ratio = colors[RED_INDEX] / float(colors[BLUE_INDEX])
    green_blue_ratio = colors[GREEN_INDEX] / float(colors[BLUE_INDEX])

    dist = 500
    best_guess = -1

    for color_index in range(6):
        rg_target = COLOR_TARGETS[color_index][sensor][0]
        rb_target = COLOR_TARGETS[color_index][sensor][1]
        gb_target = COLOR_TARGETS[color_index][sensor][2]
        curr_dist = math.sqrt((red_green_ratio - rg_target) ** 2
                              + (red_blue_ratio - rb_target) ** 2
                              + (green_blue_ratio - gb_target) ** 2)
        if curr_dist < dist:
            dist = curr_dist
            best_guess = color_index

    if best_guess is -1:
        print("Bad reading! r/g=" + str(red_green_ratio) + ", r/b=" + str(red_blue_ratio))
        return 0

    print("Guess is " + str(LED_CODES[best_guess]) + " at dist " + str(dist))
    return best_guess


def test_color_sensors():
    bm017 = ColorSensors(True)
    bm017.debug = True
    bm017.readStatus()

    bm017.isSDL_BM017There()

    bm017.getColors()
    bm017.readStatus()

    bm017.disableDevice()
    bm017.setIntegrationTimeAndGain(0x00, 0x03)

    bm017.getColors()
    bm017.readStatus()

    bm017.readStatus()

    # this will turn on the LED if LEDON is connected to INT and LEDVDD is connected to VDD_LED
    bm017.setInterrupt(True)
    time.sleep(5.0)
    bm017.setInterrupt(False)
