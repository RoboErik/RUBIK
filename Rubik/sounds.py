import os, subprocess, time
import pygame
import event

BLOOP = 0
BUZZ = 1
CHIME = 2
TICK = 3
NOTE_1 = 4
NOTE_2 = 5
NOTE_3 = 6
NOTE_4 = 7
NOTE_5 = 8
KLAXON = 9
MUSIC_BOX = 10
COUNTDOWN = 11

SOUNDS_COUNT = 12

BUTTON_SOUNDS = {
    event.EVENT_BUTTON1: NOTE_1,
    event.EVENT_BUTTON2: NOTE_2,
    event.EVENT_BUTTON3: NOTE_3,
    event.EVENT_BUTTON4: NOTE_4,
    event.EVENT_BUTTON5: NOTE_5,
}



class Sounds:
    def __init__(self):
        self._sounds = [None] * SOUNDS_COUNT
        self._initialized = False
        self._prev_button = None

    def prepare(self):
        if self._initialized:
            print("Called initialized twice!")
            return
        subprocess.call(['sudo', 'modprobe', 'snd-bcm2835'])
        time.sleep(.5)
        subprocess.call(['amixer', 'cset', "name='PCM Playback Route'", '2'])
        subprocess.call(['amixer', 'sset', "'PCM'", '100%'])
        pygame.init()
        pygame.mixer.init()

        self._sounds[BLOOP] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "bloop.wav"))
        self._sounds[BUZZ] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "buzzer.wav"))
        self._sounds[CHIME] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "chime.wav"))
        self._sounds[TICK] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "watch-tick.wav"))
        self._sounds[NOTE_1] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "4e.wav"))
        self._sounds[NOTE_2] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "3e.wav"))
        self._sounds[NOTE_3] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "3ab.wav"))
        self._sounds[NOTE_4] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "2e.wav"))
        self._sounds[NOTE_5] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "2ab.wav"))
        self._sounds[KLAXON] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "klaxon.wav"))
        self._sounds[MUSIC_BOX] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "music-box.wav"))
        self._sounds[COUNTDOWN] = pygame.mixer.Sound(os.path.join("Rubik", "Assets", "sounds", "The-Final-Countdown.ogg"))
        self._initialized = True

    def play_sound(self, sound, maxtime_ms=0, repeat=0):
        if not self._initialized:
            print("Tried to play sound without initializing")
            return
        self._sounds[sound].play(maxtime=maxtime_ms, loops=repeat)

    def stop_sound(self, sound):
        if not self._initialized:
            print("Tried to stop sound without initializing")
            return
        self._sounds[sound].stop()

    def play_button(self, button, duration=1500):
        if self._prev_button is not None:
            self._sounds[BUTTON_SOUNDS[self._prev_button]].stop()
        self.play_sound(BUTTON_SOUNDS[button], duration)
        self._prev_button = button

    def cleanup(self):
        _initialized = False
        # Cancel any playing sounds
        for i in range(len(self._sounds)):
            self.stop_sound(i)
        # Clean up the pygame components
        pygame.mixer.quit()
        pygame.quit()
