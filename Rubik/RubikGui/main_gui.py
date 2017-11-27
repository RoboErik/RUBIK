import os, time, threading, subprocess
from Queue import *
from .. import event as Events
import tkFont

try:
    from Tkinter import *

except ImportError:
    from tkinter import *

UI_QUIT = -1
UI_HOME = 00

UI_TIMER_START = 10
UI_TIMER_HOME = 10
UI_TIMER_READY = 11
UI_TIMER_RUNNING = 12
UI_TIMER_CONFIRM = 13
UI_TIMER_END = 19

UI_MATCH_START = 20
UI_MATCH_HOME = 20
UI_MATCH_READY = 21
UI_MATCH_SUCCESS = 22
UI_MATCH_FAILURE = 23
UI_MATCH_END = 29

UI_SIMON_START = 30
UI_SIMON_HOME = 30
UI_SIMON_PLAYING = 31
UI_SIMON_END = 39

_BUTTON_WIDTH = 200
_BUTTON_HEIGHT = 200


class UiCommand:
    ui_state = None
    data = None

    def __init__(self, ui_state, data=None):
        self.ui_state = ui_state
        self.data = data


class Gui():
    master_ = None
    fullscreen_ = True
    screen_on_process_ = None

    # A 1x1 pixel image for buttons displaying text. This allows their size to
    # be specified in pixels, since text only button sizes are in characters.
    pixel_icon = None

    # The icon for the pattern matching game
    match_icon = None
    # The icon for the Rubik solving game
    timer_icon = None
    # The icon for the Simon Says game
    simon_icon = None

    # The icon for resetting scores
    reset_icon = None
    # The confirmation icon
    confirm_icon = None
    # The exit/cancel icon
    cancel_icon = None

    # The icons for the standard selection buttons
    button1_icon = None
    button2_icon = None
    button3_icon = None
    button_reset_icon = None

    # Labels and their buttons appear in two rows with labels on top and the
    # corresponding button below it. Usually, the label is an icon. In some
    # screens it will be a number.

    # Label for the 1st option
    label1 = None
    # Label for the 2nd option
    label2 = None
    # Label for the 3rd option
    label3 = None
    # The icon/button showing which button to press for the 1st option
    button1 = None
    # The icon/button showing which button to press for the 2nd option
    button2 = None
    # The icon/button showing which button to press for the 3rd option
    button3 = None
    # The icon/button showing which buttons to press to reset scores
    button_reset = None

    # Queue's for communicating with other threads
    command_queue = Queue()
    event_queue = None

    button = None
    hi_there = None
    did_exit = False

    def __init__(self, master):
        self.master_ = master
        self.frame = Frame(master)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.configure_fullscreen()
        self.configure_buttons()
        self.frame.pack(fill="both", expand=True)
        self.master_.after(60000, self.exit)
        self.master_.after(100, self.poll_queue)
        self.master_.after(1000, self.turn_screen_on)

    def poll_queue(self):
        try:
            command = self.command_queue.get(False)
            if command.ui_state == UI_QUIT:
                self.exit()
            else:
                self.set_ui_state(command.ui_state, data=command.data)
            self.command_queue.task_done()
        except Empty:
            pass
        self.master_.after(100, self.poll_queue)

    def turn_screen_on(self):
        # Force the screen to turn on
        self.screen_on_process_ = subprocess.Popen('xset s reset && xset dpms force on',
                                                   shell=True)

    def configure_buttons(self):
        self.pixel_icon = PhotoImage(width=1, height=1)
        self.match_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "rubik-match.png"))
        self.timer_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "rubik-time.png"))
        self.simon_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "simon-all.png"))
        self.reset_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "reset.png"))
        self.confirm_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "confirm.png"))
        self.cancel_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "cancel.png"))

        self.button1_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "simon-1.png"))
        self.button2_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "simon-2.png"))
        self.button3_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "simon-3.png"))
        self.button_reset_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "simon-reset.png"))

        self.label1 = Label(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        self.label1.grid(row=0, column=0)
        self.label2 = Label(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        self.label2.grid(row=0, column=1)
        self.label3 = Label(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        self.label3.grid(row=0, column=2)

        self.button1 = Button(
            self.frame, image=self.button1_icon, command=self.on_press_1,
            width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT
        )
        self.button1.grid(row=1, column=0)

        # Python is the worst. To keep the button from resizing with text it
        # needs to be in a frame with pack_propagate(0). =p
        button2_frame = Frame(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        button2_frame.grid(row=1, column=1)
        button2_frame.pack_propagate(0)
        time_font = tkFont.Font(size=22)
        self.button2 = Button(
            button2_frame, image=self.button2_icon, compound="center",
            font=time_font, command=self.on_press_2,
            width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT
        )
        self.button2.pack(expand=False, fill=None)
        self.button3 = Button(
            self.frame, image=self.button3_icon, command=self.on_press_3,
            width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT
        )
        self.button3.grid(row=1, column=2)

        self.set_ui_state(UI_HOME)

    def configure_fullscreen(self):
        self.fullscreen_ = True
        self.master_.attributes("-fullscreen", True)
        self.master_.bind('<F11>', self.toggle_fullscreen)
        self.master_.bind('<Escape>', self.exit_fullscreen)

    def toggle_fullscreen(self, event):
        self.fullscreen_ = not self.fullscreen_
        self.master_.attributes("-fullscreen", self.fullscreen_)

    def exit_fullscreen(self, event):
        self.fullscreen_ = False
        self.master_.attributes("-fullscreen", self.fullscreen_)

    def set_event_queue(self, queue):
        self.event_queue = queue

    def set_ui_state(self, ui_state, data=""):
        if ui_state == UI_HOME:
            self.label1.config(image=self.timer_icon)
            self.label2.config(image=self.match_icon)
            self.label3.config(image=self.simon_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.button2_icon, text="")
            self.button3.config(image=self.button3_icon)
        elif ui_state == UI_TIMER_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.timer_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.pixel_icon, text=data)
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_MATCH_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.match_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.pixel_icon, text=data)
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_SIMON_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.simon_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.pixel_icon, text=data)
            self.button3.config(image=self.button2_icon)

    def exit(self):
        if self.did_exit:
            return
        self.screen_on_process_.kill()
        screen_off = subprocess.Popen('xset dpms force off && exit 0', shell=True)
        self.frame.quit()
        self.frame.destroy()
        time.sleep(0.5)
        screen_off.kill()
        self.did_exit = True

    def on_press_1(self):
        print("Button1 pressed")
        if self.event_queue is not None:
            event = Events.Event(Events.SOURCE_GUI, Events.EVENT_BUTTON1)
            self.event_queue.put(event)

    def on_press_2(self):
        print("Button2 pressed")
        if self.event_queue is not None:
            event = Events.Event(Events.SOURCE_GUI, Events.EVENT_BUTTON2)
            self.event_queue.put(event)

    def on_press_3(self):
        print("Button3 pressed")
        if self.event_queue is not None:
            event = Events.Event(Events.SOURCE_GUI, Events.EVENT_BUTTON3)
            self.event_queue.put(event)

    def on_press_reset(self):
        print("Reset pressed")
        if self.event_queue is not None:
            event = Events.Event(Events.SOURCE_GUI, Events.EVENT_BUTTON_RESET)
            self.event_queue.put(event)

    def get_queue(self):
        return self.command_queue

    @staticmethod
    def say_hi():
        print("hi there, everyone!")

        # root = Tk()
        #
        # app = Gui(root)
        #
        # root.mainloop()
        # root.destroy()

