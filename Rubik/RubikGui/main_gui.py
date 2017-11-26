import os, time, threading, subprocess

try:
    from Tkinter import *

except ImportError:
    from tkinter import *

UI_HOME = 00

UI_TIMER_HOME = 10
UI_TIMER_READY = 11
UI_TIMER_RUNNING = 12
UI_TIMER_CONFIRM = 13

UI_MATCH_HOME = 20
UI_MATCH_READY = 21
UI_MATCH_SUCCESS = 22
UI_MATCH_FAILURE = 23

UI_SIMON_HOME = 30
UI_SIMON_PLAYING = 31

_BUTTON_WIDTH = 200
_BUTTON_HEIGHT = 200

class Gui():
    master_ = None
    fullscreen_ = True
    screen_on_process_ = None

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

    # Callback for button presses
    callback = None

    gear_icons = []
    gear_timer = None
    exit_timer = None
    button = None
    hi_there = None

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
        self.master_.after(5000, self.exit)
        self.master_.after(1000, self.turn_screen_on)

    def turn_screen_on(self):
        # Force the screen to turn on
        self.screen_on_process_ = subprocess.Popen('xset s reset && xset dpms force on',
                                                   shell=True)

    def configure_buttons(self):
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
        self.button2 = Button(
            self.frame, image=self.button2_icon, command=self.on_press_2,
            width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT
        )
        self.button2.grid(row=1, column=1)
        self.button3 = Button(
            self.frame, image=self.button3_icon, command=self.on_press_3,
            width=_BUTTON_WIDTH, height=_BUTTON_HEIGHT
        )
        self.button3.grid(row=1, column=2)

        self.set_ui_state(UI_HOME)

        # match_icon = PhotoImage(file=os.path.join("Rubik", "Assets", "rubik-match"))
        # self.match_button = Button(
        #     self.frame, image=match_icon
        # )

        # del self.gear_icons[:]
        # self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-1.png")))
        # self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-2.png")))
        # self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-3.png")))
        # self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-4.png")))
        # self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-5.png")))
        #
        # self.button = Button(
        #     self.frame, text="QUIT", fg="red", command=self.exit
        # )
        # self.button.pack(side=LEFT)
        # self.button.config(image=self.gear_icons[0])
        # self.button.curr_gear = 0
        #
        # self.hi_there = Button(self.frame, text="Hello", command=self.say_hi)
        # self.hi_there.pack(side=LEFT)
        # image = PhotoImage(file=os.path.join("Rubik", "Assets", "rubik-time.png"))
        # self.hi_there.config(image=image)
        # self.hi_there.image = image
        #
        # self.change_gear()

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

    def set_ui_state(self, ui_state):
        if ui_state == UI_HOME:
            self.label1.config(image=self.timer_icon)
            self.label2.config(image=self.match_icon)
            self.label3.config(image=self.simon_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=self.button2_icon)
            self.button3.config(image=self.button3_icon)
        elif ui_state == UI_TIMER_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.timer_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=None, text="02:55.44")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_MATCH_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.match_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=None, text="02:55.44")
            self.button3.config(image=self.button2_icon)
        elif ui_state == UI_SIMON_HOME:
            self.label1.config(image=self.confirm_icon)
            self.label2.config(image=self.simon_icon)
            self.label3.config(image=self.cancel_icon)
            self.button1.config(image=self.button1_icon)
            self.button2.config(image=None, text="42")
            self.button3.config(image=self.button2_icon)

    # def change_gear(self):
    #     self.button.curr_gear = (self.button.curr_gear + 1) % len(self.gear_icons)
    #     self.button.config(image=self.gear_icons[self.button.curr_gear])
    #     self.gear_timer = threading.Timer(0.1, self.change_gear)
    #     self.gear_timer.start()

    def exit(self):
        self.screen_on_process_.kill()
        screen_off = subprocess.Popen('xset dpms force off && exit 0', shell=True)
        #self.gear_timer.cancel()
        self.frame.quit()
        #self.button.destroy()
        #self.hi_there.destroy()
        self.frame.destroy()
        time.sleep(0.5)
        screen_off.kill()

    def on_press_1(self):
        print("Button1 pressed")
        self.callback.on_press(1)

    def on_press_2(self):
        print("Button2 pressed")
        self.callback.on_press(2)

    def on_press_3(self):
        print("Button3 pressed")
        self.callback.on_press(3)

    def on_press_reset(self):
        print("Reset pressed")
        self.callback.on_press(9)

    @staticmethod
    def say_hi():
        print("hi there, everyone!")

        # root = Tk()
        #
        # app = Gui(root)
        #
        # root.mainloop()
        # root.destroy()


class Callback:
    def __init__(self):
        pass

    def on_press(self, which):
        raise NotImplementedError("Must implement on_press(which)")
