import os, subprocess, threading
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

SOUNDS_COUNT = 9

BUTTON_SOUNDS = {
    event.EVENT_BUTTON1: NOTE_1,
    event.EVENT_BUTTON2: NOTE_2,
    event.EVENT_BUTTON3: NOTE_3,
    event.EVENT_BUTTON4: NOTE_4,
    event.EVENT_BUTTON5: NOTE_5,
}



class Sounds:
    def __init__(self):
        self._intervals = [0] * SOUNDS_COUNT
        self._timers = [None] * SOUNDS_COUNT
        self._sounds = [None] * SOUNDS_COUNT
        self._initialized = False
        self._prev_button = None

    def prepare(self):
        if self._initialized:
            print("Called initialized twice!")
            return
        subprocess.call(['amixer', 'cset', "name='PCM Playback Route'", '2'])
        subprocess.call(['sudo', 'modprobe', 'snd-bcm2835'])
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
        self._initialized = True

    def play_sound(self, sound, maxtime_ms=0):
        if not self._initialized:
            print("Tried to play sound without initializing")
            return
        self._sounds[sound].play(maxtime=maxtime_ms)

    def play_button(self, button, duration=1500):
        if self._prev_button is not None:
            self._sounds[BUTTON_SOUNDS[self._prev_button]].stop()
        self.play_sound(BUTTON_SOUNDS[button], duration)
        self._prev_button = button

    def _repeat_sound_internal(self, sound):
        if not self._initialized:
            return
        interval = self._intervals[sound]
        timer = self._timers[sound]

        if timer is not None:
            timer.cancel()
        if interval == 0:
            return
        self.play_sound(sound)

        timer = threading.Timer(interval, self._repeat_sound_internal, [sound])
        self._timers[sound] = timer
        timer.start()

    def repeat_sound(self, sound, interval):
        if not self._initialized:
            print ("Tried to repeat sound without initializing")
            return
        self._intervals[sound] = interval
        self._repeat_sound_internal(sound)

    def cleanup(self):
        _initialized = False
        # Cancel any sound timers
        for i in range(len(self._intervals)):
            self.repeat_sound(i, 0)
        # Clean up the pygame components
        pygame.mixer.quit()
        pygame.quit()
