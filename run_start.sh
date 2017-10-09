#!/usr/bin/env bash

# Runs the Rubik program on boot. Don't try to run manually
echo "Still running..."
export DISPLAY=":0.0"
xhost +
# xset s reset && xset dpms force on # Force the screen to wake up

# Change the path to where you've placed the RUBIK code.
cd /home/pi/pywork/RUBIK/
sudo PYTHONPATH=".:Rubik/RubikSolver/rpi_ws281x/python/build/lib.linux-armv6l-2.7" python RubikRunner.py
