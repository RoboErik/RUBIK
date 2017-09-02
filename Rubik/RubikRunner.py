from Rubik.GearRatios import gear_ratios
from Rubik.SimonSays import simon_says
from Rubik import utils

simonSays = simon_says.SimonSays()

gearRatio = gear_ratios.GearRatio()

print("Type s for SimonSays, g for GearRatio")
nextChar = utils.getChar()
if nextChar.upper() == 'S':
    simonSays.start()
elif nextChar.upper() == 'G':
    gearRatio.start()
