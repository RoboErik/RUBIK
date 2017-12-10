'''
    File: midiExample

    Author: Jeff Kinne

    Contents:  basic example showing how to play midi sounds using pygame.

    Requires:  this example was run in Python 2.7 with pygame 1.9.2 installed.

    Sources:  I took the pygame.examples.midi file and extracted out only
    what is needed to play a few notes.
'''

import pygame
import pygame.midi
import subprocess
from time import sleep


def midiExample():
    # Things to consider when using pygame.midi:
    #
    # 1) Initialize the midi module with a to pygame.midi.init().
    # 2) Create a midi.Output instance for the desired output device port.
    # 3) Select instruments with set_instrument() method calls.
    # 4) Play notes with note_on() and note_off() method calls.
    # 5) Call pygame.midi.Quit() when finished. Though the midi module tries
    #    to ensure that midi is properly shut down, it is best to do it
    #    explicitly. A try/finally statement is the safest way to do this.
    #
    GRAND_PIANO = 0
    CHURCH_ORGAN = 19
    instrument = CHURCH_ORGAN
    # instrument = GRAND_PIANO
    #amixer cset name='PCM Playback Route' 2
    subprocess.call(['amixer', 'cset', "name='PCM Playback Route'", '2'])
    # subprocess.call(['mpg123', 'Rubik/Assets/739823_Blues-By-Bedtime.mp3'])

    pygame.init()
    pygame.midi.init()

    port = pygame.midi.get_default_output_id()
    print ("using output_id :%s:" % port)
    midi_out = pygame.midi.Output(0, 1)
    try:
        midi_out.set_instrument(instrument, 1)

        midi_out.note_on(72, 127, 1)  # 74 is middle C, 127 is "how loud" - max is 127
        sleep(.5)
        midi_out.note_off(72, 127, 1)
        sleep(.5)

        midi_out.note_on(76, 127, 1)  # E
        sleep(.5)
        midi_out.note_off(76, 127, 1)
        sleep(.5)

        midi_out.note_on(79, 127)  # G
        sleep(.5)
        midi_out.note_off(79, 127)
        sleep(.5)

        midi_out.note_on(72, 127)
        midi_out.note_on(76, 127)
        midi_out.note_on(79, 127)
        sleep(.5)
        midi_out.note_off(72, 127)
        midi_out.note_off(76, 127)
        midi_out.note_off(79, 127)

    finally:
        del midi_out
        pygame.midi.quit()
        pygame.quit()

