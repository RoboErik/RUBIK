import os, time, threading, subprocess
from Queue import *
from .. import event as Events
from .. import queue_common
import tkFont

try:
    from Tkinter import *

except ImportError:
    from tkinter import *

Command = queue_common.Command

UI_QUIT = -1
UI_HOME = 00
UI_CONFIRM_RESET = 99

UI_TIMER_START = 10
UI_TIMER_HOME = 10
UI_TIMER_READY = 11
UI_TIMER_RUNNING = 12
UI_TIMER_CONFIRM = 13
UI_TIMER_END = 19

UI_MATCH_START = 20
UI_MATCH_HOME = 20
UI_MATCH_READY = 21
UI_MATCH_PLAYING = 22
UI_MATCH_END = 29

UI_SIMON_START = 30
UI_SIMON_HOME = 30
UI_SIMON_PLAYING = 31
UI_SIMON_END = 39

_BUTTON_WIDTH = 200
_BUTTON_HEIGHT = 200
_SCREEN_WIDTH = 640
_SCREEN_HEIGHT = 480


class Gui(queue_common.QueueCommon):

    def __init__(self, master):
        self.master_ = None
        self.fullscreen_ = True
        self.screen_on_process_ = None
        self.font = tkFont.Font(size=22)

        # A 1x1 pixel image for buttons displaying text. This allows their size to
        # be specified in pixels, since text only button sizes are in characters.
        self.pixel_icon = None

        # The icon for the pattern matching game
        self.match_icon = None
        # The icon for the Rubik solving game
        self.timer_icon = None
        # The icon for the Simon Says game
        self.simon_icon = None

        # The icon for resetting scores
        self.reset_icon = None
        # The confirmation icon
        self.confirm_icon = None
        # The exit/cancel icon
        self.cancel_icon = None

        # The icons for the standard selection buttons
        self.button1_icon = None
        self.button2_icon = None
        self.button3_icon = None
        self.button_reset_icon = None

        # Labels and their buttons appear in two rows with labels on top and the
        # corresponding button below it. Usually, the label is an icon. In some
        # screens it will be a number.

        # Label for the 1st option
        self.label1 = None
        # Label for the 2nd option
        self.label2 = None
        # Label for the 3rd option
        self.label3 = None
        # The icon/button showing which button to press for the 1st option
        self.button1 = None
        # The icon/button showing which button to press for the 2nd option
        self.button2 = None
        # The icon/button showing which button to press for the 3rd option
        self.button3 = None
        # The icon/button showing which buttons to press to reset scores
        self.button_reset = None

        self.button = None
        self.hi_there = None
        self.did_exit = False

        self.master_ = master
        self.frame = Frame(master, width=_SCREEN_WIDTH, height=_SCREEN_HEIGHT)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.pack(fill="both", expand=True)
        self.frame.pack_propagate(0)
        self.configure_fullscreen()
        self.configure_buttons()
        # self.master_.after(60000, self.exit)
        self.master_.after(100, self.poll_queue)
        self.master_.after(1000, self.turn_screen_on)
        queue_common.QueueCommon.__init__(self)

    def poll_queue(self):
        self.check_queue()
        self.master_.after(100, self.poll_queue)

    def handle_command(self, command):
        # print("Handling Gui command with state " + str(command.command))
        if command.command == UI_QUIT:
            self.exit()
        else:
            self.set_ui_state(command.command, data=command.data, data2=command.data2)

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

        self.create_labels()
        self.create_buttons2()

        self.set_ui_state(UI_HOME)

    def create_labels(self):
        # Python is the worst. To keep the button from resizing with text it
        # needs to be in a frame with pack_propagate(0). =p
        frame = Frame(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        frame.grid(row=0, column=0)
        frame.pack_propagate(0)
        self.label1 = Label(frame, width=_BUTTON_WIDTH-10, height=_BUTTON_HEIGHT,
                            compound="center", font=self.font)
        self.label1.bind('<Button-1>', self.on_press_1)
        self.label1.pack()

        frame = Frame(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        frame.grid(row=0, column=1)
        frame.pack_propagate(0)
        self.label2 = Label(frame, width=_BUTTON_WIDTH-20, height=_BUTTON_HEIGHT,
                            compound="center", font=self.font)
        self.label2.bind('<Button-1>', self.on_press_2)
        self.label2.pack()

        frame = Frame(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        frame.grid(row=0, column=2)
        frame.pack_propagate(0)
        self.label3 = Label(frame, width=_BUTTON_WIDTH+20, height=_BUTTON_HEIGHT,
                            compound="center", font=self.font)
        self.label3.bind('<Button-1>', self.on_press_3)
        self.label3.pack()

    # Creates a set of labels which can be used as buttons.
    def create_buttons2(self):
        # Python is the worst. To keep the button from resizing with text it
        # needs to be in a frame with pack_propagate(0). =p
        # The row and column are reversed because the screen is upside down.
        frame = Frame(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        frame.grid(row=1, column=0)
        frame.pack_propagate(0)
        self.button1 = Label(frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT,
                             compound="center", font=self.font)
        self.button1.bind('<Button-1>', self.on_press_1)
        self.button1.pack()

        frame = Frame(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        frame.grid(row=1, column=1)
        frame.pack_propagate(0)
        self.button2 = Label(frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT,
                             compound="center", font=self.font)
        self.button2.bind('<Button-1>', self.on_press_2)
        self.button2.pack()

        frame = Frame(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        frame.grid(row=1, column=2)
        frame.pack_propagate(0)
        self.button3 = Label(frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT,
                             compound="center", font=self.font)
        self.button3.bind('<Button-1>', self.on_press_3)
        self.button3.pack()

    # Creates a set of actual buttons and positions them.
    def create_buttons(self):
        self.button1 = Button(
            self.frame, image=self.button1_icon, command=self.on_press_1,
            width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT, borderwidth=0
        )
        self.button1.grid(row=0, column=2)
        # Python is the worst. To keep the button from resizing with text it
        # needs to be in a frame with pack_propagate(0). =p
        button2_frame = Frame(self.frame, width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT)
        button2_frame.grid(row=0, column=1)
        button2_frame.pack_propagate(0)
        time_font = tkFont.Font(size=22)
        self.button2 = Button(
            button2_frame, image=self.button2_icon, compound="center",
            font=time_font, command=self.on_press_2,
            width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT, borderwidth=0
        )
        self.button2.pack(expand=False, fill=None)
        self.button3 = Button(
            self.frame, image=self.button3_icon, command=self.on_press_3,
            width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT, borderwidth=0
        )
        self.button3.grid(row=0, column=0)

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

    def set_ui_state(self, ui_state, data="", data2=""):
        if ui_state == UI_HOME:
            self.label1.config(image=self.timer_icon)
            self.label2.config(image=self.match_icon)
            self.label3.config(image=self.simon_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.button3_icon, text="")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_TIMER_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.timer_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.pixel_icon, text=data, fg="black")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_MATCH_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.match_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.pixel_icon, text=data, fg="black")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_SIMON_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.simon_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.pixel_icon, text=data, fg="black")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_TIMER_RUNNING or ui_state == UI_TIMER_READY:
            self.label1.config(image=self.pixel_icon)
            self.label2.config(image=self.timer_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.pixel_icon)
            self.button2.config(image=self.pixel_icon, text=data2, fg="red")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_MATCH_PLAYING or ui_state == UI_MATCH_READY:
            self.label1.config(image=self.pixel_icon)
            self.label2.config(image=self.match_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.pixel_icon)
            self.button2.config(image=self.pixel_icon, text=data2, fg="red")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_SIMON_PLAYING:
            self.label1.config(image=self.pixel_icon)
            self.label2.config(image=self.simon_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.pixel_icon)
            self.button2.config(image=self.pixel_icon, text=data2, fg="red")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_TIMER_CONFIRM:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.timer_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.pixel_icon, text=data2, fg="green")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_CONFIRM_RESET:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.reset_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button_reset_icon)
            self.button2.config(image=self.pixel_icon, text="")
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

    def on_press_1(self, e):
        print("Button1 pressed")
        event = Events.Event(Events.SOURCE_GUI, Events.EVENT_BUTTON1)
        self.send_event(event)

    def on_press_2(self, e):
        print("Button2 pressed")
        event = Events.Event(Events.SOURCE_GUI, Events.EVENT_BUTTON2)
        self.send_event(event)

    def on_press_3(self, e):
        print("Button3 pressed")
        event = Events.Event(Events.SOURCE_GUI, Events.EVENT_BUTTON3)
        self.send_event(event)

    def on_press_reset(self, e):
        print("Reset pressed")
        event = Events.Event(Events.SOURCE_GUI, Events.EVENT_BUTTON_RESET)
        self.send_event(event)
