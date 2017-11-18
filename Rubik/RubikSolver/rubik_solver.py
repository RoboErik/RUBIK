import threading
import RPi.GPIO as GPIO
import time
from . import switch_timer
from .. import utils
from .. import pins

# For reading the color sensors
from color_sensors import ColorSensors

from .rpi_ws281x.python.neopixel import *

# LED strip configuration:
LED_COUNT = 9  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 5  # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP = ws.WS2811_STRIP_GRB  # Strip type and colour ordering

# In this mode just records the time between lifting and replacing the Cube.
MODE_TIME = 0
# In this mode generates a pattern and checks for that pattern on down.
MODE_PATTERN = 1

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS,
                          LED_CHANNEL, LED_STRIP)
strip.begin()

color_sensors = None


# Does not solve a Rubik cube, but either times how long it took to solve or
# requires a specific pattern be created.
class RubikSolver(threading.Thread):
    _state = 0
    _mode = MODE_TIME
    _pattern = []
    _result = []

    _timer = switch_timer.SwitchTimer()
    _stop_event = threading.Event()

    def set_mode(self, mode):
        _mode = mode

    def show_pattern(self):
        return

    def hide_pattern(self):
        return

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
        print("Pin set up")

    def _teardown(self):
        print("Teardown of RubikSolver")
        GPIO.remove_event_detect(pins.RUBIK_CUBE_SWITCH)
        self.hide_pattern()

    def stop(self):
        print("Stopping RubikSolver! Time is " + str(utils.curr_time_s()))
        self._stop_event.set()

    def run(self):
        self._setup()
        #rainbow(strip)
        #strip.setBrightness(0)

        # strip.setPixelColor(1, 0xaa00aa)
        # strip.show()
        # self._stop_event.wait(6)
        # strip.setPixelColor(1, 0x000000)

#        test_color_sensors()
        color_sensors = ColorSensors()
        set_all_leds(strip, Color(80, 60, 40))

        incr_brightness = False
        brightness = -20 if incr_brightness else 80
        for i in range(99):
            sensor = i % 9
            if incr_brightness:
                if sensor is 0:
                    brightness += 20
                    print("\n")
                set_all_leds(strip, Color(brightness, brightness, brightness))
            color_sensors.set_sensor(sensor)
            colors = color_sensors.getColors()
            guess = str(guess_color(colors))
            print(guess + " guessed at brightness " + str(brightness) + " Colors " + str(sensor) + ": " + str(colors))
            time.sleep(.1)
        set_all_leds(strip, 0)
        color_sensors.clear_active()
        self._teardown()

def guess_color(colors):
    CLEAR = 0
    RED = 1
    GREEN = 2
    BLUE = 3

    if colors[CLEAR] < 100:
        return "none"

    red_green_ratio = colors[RED]/float(colors[GREEN])
    red_blue_ratio = colors[RED]/float(colors[BLUE])
    green_blue_ratio = colors[GREEN]/float(colors[BLUE])
    ratio_string = " r/g=" + str(red_green_ratio) + " r/b=" + str(red_blue_ratio)

    if 0.9 < red_green_ratio < 1.1:
        if 0.9 < red_blue_ratio < 1.1:
            return "white" + ratio_string

    if red_green_ratio > 1.5:
        if red_blue_ratio > 1.2:
            return "red" + ratio_string

    return "unknown r/g=" + str(red_green_ratio) + " r/b=" + str(red_blue_ratio)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def set_all_leds(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color & 0xffffff)
    strip.show()

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


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