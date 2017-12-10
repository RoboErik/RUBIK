import os, subprocess
import pygame

subprocess.call(['amixer', 'cset', "name='PCM Playback Route'", '2'])
subprocess.call(['sudo', 'modprobe', 'snd-bcm2835'])
pygame.init()
pygame.mixer.init()

sounda= pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "bloop_x.wav"))


def play_bloop():
    sounda.play()


def cleanup():
    pygame.mixer.quit()
    pygame.quit()
