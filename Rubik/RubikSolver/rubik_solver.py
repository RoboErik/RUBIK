import threading
import RPi.GPIO as GPIO
import time
import random
from . import switch_timer
from .. import utils
from .. import pins

# For reading the color sensors
from color_sensors import ColorSensors
from leds import LedStrip

from .rpi_ws281x.python.neopixel import *

# In this mode just records the time between lifting and replacing the Cube.
MODE_TIME = 0
# In this mode generates a pattern and checks for that pattern on down.
MODE_PATTERN = 1

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
LED_SENSOR_BRIGHTNESS = 75

# Does not solve a Rubik cube, but either times how long it took to solve or
# requires a specific pattern be created.
class RubikSolver(threading.Thread):
    _state = 0
    _mode = MODE_TIME
    _pattern = []
    _result = []

    _timer = switch_timer.SwitchTimer()
    _stop_event = threading.Event()
    color_sensors = None
    led_strip = None

    def set_mode(self, mode):
        _mode = mode

    def generate_pattern(self):
        self._pattern = []
        for i in range(9):
            self._pattern.append(LED_CODES[random.randint(0, 5)])

    def show_pattern(self):
        self.led_strip.set_brightness(LED_PATTERN_BRIGHTNESS)
        for i in range(len(self._pattern)):
            self.led_strip.set_led(i, LED_COLORS[LED_CODES.index(self._pattern[i])])
        return

    def hide_pattern(self):
        self.led_strip.set_all_leds(0)
        return

    def read_colors(self):
        self.led_strip.set_brightness(LED_SENSOR_BRIGHTNESS)
        self.led_strip.set_all_leds(LED_SENSOR_COLOR)
        results = []
        for i in range(9):
            results.append(self._read_color(i))
        return results

    def _read_color(self, index):
        self.color_sensors.set_sensor(index)
        colors = self.color_sensors.getColors()
        guess = guess_color(colors)
        return guess

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
        self.color_sensors = ColorSensors()
        self.led_strip = LedStrip()
        self.led_strip.set_all_leds(Color(80, 60, 60))

    def _teardown(self):
        print("Teardown of RubikSolver")
        GPIO.remove_event_detect(pins.RUBIK_CUBE_SWITCH)

        self.color_sensors.clear_active()
        self.hide_pattern()

        # Is this cleanup necessary?
        del self.led_strip
        self.led_strip = None
        del self.color_sensors
        self.color_sensors = None

    def stop(self):
        print("Stopping RubikSolver! Time is " + str(utils.curr_time_s()))
        self._stop_event.set()

    def run(self):
        self._setup()

        # self.test_pattern_display()

        csv = open("csv_colors.txt", 'w')
        self.collect_color_data(csv)
        csv.close()

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

    def collect_color_data(self, csv):
        self.led_strip.set_brightness(LED_SENSOR_BRIGHTNESS)
        self.led_strip.set_all_leds(LED_SENSOR_COLOR)
        incr_brightness = False
        brightness = -5 if incr_brightness else LED_SENSOR_BRIGHTNESS
        csv.write("Sensor, Red/Green ratio, Red/Blue ratio, Green/Blue ratio, sample\n")
        for i in range(99):
            sensor = i % 9
            if sensor is 0:
                print("\nSAMPLE " + str(i/9) + ":\n")
                if incr_brightness:
                    brightness += 10
                    self.led_strip.set_brightness(brightness)
            # self.color_sensors.set_sensor(sensor)
            # colors = self.color_sensors.getColors()
            guess = self._read_color(sensor)
            csv.write(str(sensor) + ", " + guess + ", " + str(i) + "\n")
            print(str(sensor) + ": " + guess + " at Brightness=" + str(brightness))
            time.sleep(.1)


def guess_color(colors):
    CLEAR = 0
    RED = 1
    GREEN = 2
    BLUE = 3

    if colors[CLEAR] < 10 or colors[GREEN] < 10 or colors[BLUE] < 10:
        return "none, none, none"

    red_green_ratio = colors[RED]/float(colors[GREEN])
    red_blue_ratio = colors[RED]/float(colors[BLUE])
    green_blue_ratio = colors[GREEN]/float(colors[BLUE])
    ratio_string = str(red_green_ratio) + ", " + str(red_blue_ratio) + ", " + str(green_blue_ratio)

    if True:
        return ratio_string

    if 0.9 < red_green_ratio < 1.1:
        if 0.9 < red_blue_ratio < 1.1:
            return "white" + ratio_string

    if red_green_ratio > 1.5:
        if red_blue_ratio > 1.2:
            return "red" + ratio_string

    return "unknown r/g=" + str(red_green_ratio) + " r/b=" + str(red_blue_ratio)




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