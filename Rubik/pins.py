import RPi.GPIO as GPIO


RUBIK_CUBE_SWITCH = 23

def setup():
    GPIO.setmode(GPIO.BCM)

    # GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.
    # Both ports are wired to connect to GND on button press.
    # So we'll be setting up falling edge detection for both
    GPIO.setup(RUBIK_CUBE_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # GPIO 24 set up as an input, pulled down, connected to 3V3 on button press
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def teardown():
    GPIO.cleanup()