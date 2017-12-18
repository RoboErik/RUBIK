import RPi.GPIO as GPIO

# GPIO 27
SW0_LED = 13
# GPIO 22
SW0_IN = 15

# GPIO 23
SW1_LED = 16
# GPIO 24
SW1_IN = 18

# GPIO 10
SW2_LED = 19
# GPIO 09
SW2_IN = 21

# GPIO 25
SW3_LED = 22
# GPIO 11
SW3_IN = 23

# GPIO 08
SW4_LED = 24
# GPIO 07
SW4_IN = 26

# GPIO 12
ENC0 = 32
# GPIO 13
ENC1 = 33


def setup():
    GPIO.setmode(GPIO.BOARD)

    # Input pins
    GPIO.setup(SW0_IN, GPIO.IN)
    GPIO.setup(SW1_IN, GPIO.IN)
    GPIO.setup(SW2_IN, GPIO.IN)
    GPIO.setup(SW3_IN, GPIO.IN)
    GPIO.setup(SW4_IN, GPIO.IN)
    GPIO.setup(ENC0, GPIO.IN)
    GPIO.setup(ENC1, GPIO.IN)

    # Output pins
    GPIO.setup(SW0_LED, GPIO.OUT)
    GPIO.setup(SW1_LED, GPIO.OUT)
    GPIO.setup(SW2_LED, GPIO.OUT)
    GPIO.setup(SW3_LED, GPIO.OUT)
    GPIO.setup(SW4_LED, GPIO.OUT)


def teardown():
    GPIO.cleanup()
