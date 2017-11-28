import threading
import RPi.GPIO as GPIO
import time
import random
import math
from . import switch_timer
from .. import utils
from .. import pins
from .. import queue_common

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
TEST_PATTERN = ['W', 'G', 'B', 'Y', 'O', 'R', 'Y', 'O', 'R']
LED_PATTERN_BRIGHTNESS = 20

LED_SENSOR_COLOR = Color(255, 235, 130)
LED_SENSOR_BRIGHTNESS = 15

# All the target arrays in one big array
COLOR_TARGETS = COLOR_TARGETS_15


# Does not solve a Rubik cube, but either times how long it took to solve or
# requires a specific pattern be created.
class RubikSolver(threading.Thread, queue_common.QueueCommon):

    def __init__(self):
        self. _state = 0
        self._mode = MODE_TEST  # TODO Change to idle
        self._pattern = []
        self._result = []

        self._timer = switch_timer.SwitchTimer()
        self._stop_event = threading.Event()
        self._color_sensors = None
        self._led_strip = None
        threading.Thread.__init__(self)
        queue_common.QueueCommon.__init__(self)

    def handle_command(self, command):
        if command.command == COMMAND_SET_MODE:
            self._mode = command.data

    def generate_pattern(self):
        self._pattern = []
        for i in range(9):
            self._pattern.append(LED_CODES[random.randint(0, 5)])

    def show_pattern(self):
        self._led_strip.set_brightness(LED_PATTERN_BRIGHTNESS)
        for i in range(len(self._pattern)):
            self._led_strip.set_led(i, LED_COLORS[LED_CODES.index(self._pattern[i])])
        return

    def hide_pattern(self):
        self._led_strip.set_brightness(0)
        self._led_strip.set_all_leds(0)
        return

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
        # self.hide_pattern()
        return results

    def _read_color(self, index):
        self._color_sensors.set_sensor(index)
        colors = self._color_sensors.getColors()
        return colors

    def _switch_callback(self, channel):
        if GPIO.input(pins.RUBIK_CUBE_SWITCH):
            if (self._mode == MODE_PATTERN):
                self.show_pattern()
            self._timer.on_switch_up()
        else:
            self._timer.on_switch_down()

    def _setup(self):
        print("Setup of RubikSolver")
        GPIO.add_event_detect(pins.RUBIK_CUBE_SWITCH, GPIO.BOTH, callback=self._switch_callback,
                              bouncetime=300)
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
                time.sleep(0.1)
            self.check_queue()
            self._teardown()

    def test_pattern_display(self):
        self._pattern = TEST_PATTERN
        self.show_pattern()
        utils.getChar()
        self.hide_pattern()
        self.generate_pattern()
        self.show_pattern()
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
