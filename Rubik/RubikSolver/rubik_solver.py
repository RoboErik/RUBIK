import threading
import RPi.GPIO as GPIO
import time
from . import switch_timer
from .. import utils
from .. import pins

# For reading the color sensors
import smbus
from SDL_BM017CS.Adafruit_I2C import Adafruit_I2C
from SDL_BM017CS.SDL_PC_BM017CS import SDL_BM017

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

# I2C Bus for the color sensors
bus = smbus.SMBus(1)
address = 0x70


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

        test_color_sensors()
        bm017 = SDL_BM017(True)
        bm017.debug = False
        set_all_leds(strip, 255)
        for i in range(100):
            print("Colors " + str(i) + ": " + str(bm017.getColors()))
            time.sleep(.1)
        set_all_leds(strip, 0)
        self._teardown()


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def set_all_leds(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color & 255)
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
    bm017 = SDL_BM017(True)
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