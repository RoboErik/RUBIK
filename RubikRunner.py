#!/usr/bin/python3
import time

from Rubik.GearRatios import gear_ratios
from Rubik.SimonSays import simon_says
from Rubik.Timer import rubik_solver
from Rubik import utils
from Rubik import pins

pins.setup()
# Set up puzzle threads
simonSays = simon_says.SimonSays()
gearRatio = gear_ratios.GearRatio()
rubikSolver = rubik_solver.RubikSolver()

print("Type s for SimonSays, g for GearRatio, r for RubikSolver.")
nextChar = utils.getChar()
active = []

if nextChar.upper() == 'S':
    simonSays.start()
    active.append(simonSays)
elif nextChar.upper() == 'G':
    gearRatio.start()
    active.append(gearRatio)
elif nextChar.upper() == 'R':
    rubikSolver.start()
    time.sleep(3)  # TODO remove
    rubikSolver.stop()
    active.append(rubikSolver)

print("Waiting for threads to finish\n")
for thread in active:
    thread.join()
print("Threads have finished")

pins.teardown()
