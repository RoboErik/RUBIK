import RPi.GPIO as GPIO
import time

from .rpi_ws281x.python.neopixel import *

LOG = False

class LedStrip:
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

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS,
                              LED_CHANNEL, LED_STRIP)
    strip.begin()

    def set_led(self, led, color):
        if LOG:
            print("Setting led " + str(led) + " to " + str(color))
        if 0 <= led < self.LED_COUNT:
            self.strip.setPixelColor(led, color & 0xffffff)
            self.strip.show()
        else:
            print("led " + str(led) + " does not exist")

    def set_all_leds(self, color):
        if LOG:
            print("Setting all leds to " + str(color))
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color & 0xffffff)
        self.strip.show()

    def set_brightness(self, brightness):
        if LOG:
            print("Setting brightness to " + str(brightness))
        self.strip.setBrightness(brightness)
        self.strip.show()

    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    @staticmethod
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
