#!/usr/bin/python
import time
import subprocess

from Rubik.GearRatios import gear_ratios
from Rubik.SimonSays import simon_says
#
from Rubik.RubikGui import main_gui
from Rubik import utils

pins_setup = False

try:
    # for running on the Pi
    import Tkinter as tkinter
    from Rubik.RubikSolver import rubik_solver
    rubikSolver = rubik_solver.RubikSolver()
    from Rubik import pins
    pins.setup()
    pins_setup = True

except ImportError:
    print("Not on Pi, solver/pins unavailable")
    import tkinter


root = tkinter.Tk()
running = True

#while running:
for x in range(0, 2):
    active = []

    # Set up puzzle threads
    simonSays = simon_says.SimonSays()
    gearRatio = gear_ratios.GearRatio()


    print("Type s for SimonSays, g for GearRatio, r for RubikSolver.")
    nextChar = 'G'  # utils.getChar()

    if nextChar.upper() == 'S':
        simonSays.start()
        active.append(simonSays)
    elif nextChar.upper() == 'G':
        gearRatio.start()
        active.append(gearRatio)
    elif nextChar.upper() == 'R':
        rubikSolver.start()
        print("sleeping for 3\n")
        time.sleep(3)  # TODO remove
        print("done sleeping\n")
        rubikSolver.stop()
        active.append(rubikSolver)

    # Start the UI thread
    gui = main_gui.Gui(root)
    root.mainloop()
    print("Waiting for threads to finish\n")
    for thread in active:
        thread.join()
    print("Threads have finished. Run again? Y/N")
    nextChar = 'N'  # utils.getChar()
    if nextChar.upper() != 'Y':
        running = False

root.destroy()
if pins_setup:
    pins.teardown()

print("Kill")