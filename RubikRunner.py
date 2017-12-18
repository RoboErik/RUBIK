#!/usr/bin/python
import time
import subprocess

from Rubik.GearRatios import gear_ratios
from Rubik.SimonSays import simon_says
#
from Rubik.RubikGui import main_gui
from Rubik import utils
from Rubik import state_controller

pins_setup = False
TEST_MODE = True

try:
    # for running on the Pi
    import Tkinter as tkinter
    from Rubik.RubikSolver import rubik_solver
    from Rubik import pins
    pins.setup()
    pins_setup = True

except ImportError:
    print("Not on Pi, solver/pins unavailable")
    import tkinter

root = tkinter.Tk()
running = True

try:
    while running:
        active = []

        # Set up puzzle threads
        gui = main_gui.Gui(root)
        simonSays = simon_says.SimonSays()
        gearRatio = gear_ratios.GearRatio()
        rubikSolver = rubik_solver.RubikSolver()

        stateController = state_controller.StateController(gui, rubikSolver, simonSays, gearRatio)
        start_ui = True

        if TEST_MODE:
            print("Type s for SimonSays, g for GearRatio, r for RubikSolver, u for UI. b to Toggle buttons")
            #nextChar = 'G'
            nextChar = utils.getChar()

            if nextChar.upper() == 'S':
                simonSays.start()
                active.append(simonSays)
            elif nextChar.upper() == 'G':
                gearRatio.start()
                active.append(gearRatio)
            elif nextChar.upper() == 'R':
                rubikSolver.start()
                active.append(rubikSolver)
            elif nextChar.upper() == 'U':
                stateController.start()
                active.append(stateController)
            elif nextChar.upper() == 'B':
                utils.use_buttons = not utils.use_buttons
                print("set using buttons to " + str(utils.use_buttons))
                start_ui = False
        else:
            utils.use_buttons = True
            stateController.start()
            active.append(stateController)

        if start_ui:
            # Start the UI thread
            root.mainloop()
        print("Waiting for threads to finish\n")
        for thread in active:
            thread.join()

        if TEST_MODE:
            print("Threads have finished. Run again? Y/N")
            # nextChar = 'N'  # utils.getChar()
            nextChar = utils.getChar()
            if nextChar.upper() != 'Y':
                running = False

    root.destroy()
    if pins_setup:
        pins.teardown()
except KeyboardInterrupt:
    root.destroy()
    pins.teardown()
    print("Kill")
    subprocess.Popen('sudo killall python', shell=True)