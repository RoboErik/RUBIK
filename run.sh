#!/usr/bin/env bash

# Runs the Rubik program when called from the command line.
# Use this version for testing over ssh.
echo "Running..."
export DISPLAY=":0.0"
xhost +
# xset s reset && xset dpms force on # Force the screen to wake up
sudo PYTHONPATH=".:Rubik/RubikSolver/rpi_ws281x/python/build/lib.linux-armv6l-2.7" python RubikRunner.py
