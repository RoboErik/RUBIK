#!/usr/bin/python
import time
import tkinter

from Rubik.GearRatios import gear_ratios
from Rubik.SimonSays import simon_says
#
from Rubik.RubikGui import main_gui
from Rubik import utils

try:
    # for running on the Pi
    from Rubik.RubikSolver import rubik_solver
    rubikSolver = rubik_solver.RubikSolver()
    from Rubik import pins
    pins.setup()

except ImportError:
    print("Not on Pi, solver unavailable")

active = []


# Set up puzzle threads
simonSays = simon_says.SimonSays()
gearRatio = gear_ratios.GearRatio()


print("Type s for SimonSays, g for GearRatio, r for RubikSolver.")
nextChar = utils.getChar()

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
root = tkinter.Tk()
gui = main_gui.Gui(root)
root.mainloop()
print("Waiting for threads to finish\n")
for thread in active:
    thread.join()
print("Threads have finished")

root.destroy()
pins.teardown()
