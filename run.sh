#!/usr/bin/env bash

export DISPLAY=":0.0" # configure the display
xhost + # enable xhost?
xset s reset && xset dpms force on # Force the screen to wake up
sudo PYTHONPATH=".:Rubik/RubikSolver/rpi_ws281x/python/build/lib.linux-armv6l-2.7" python RubikRunner.py
