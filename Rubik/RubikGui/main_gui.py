import os, time, threading
import Queue

try:
    from Tkinter import *

except ImportError:
    from tkinter import *

class Gui():
    master_ = None
    fullscreen_ = True
    callback_queue = Queue.Queue()

    gear_icons = []
    gear_timer = None
    exit_timer = None
    button = None
    hi_there = None

    def __init__(self, master):
        self.master_ = master
        self.frame = Frame(master)
        self.frame.pack()
        self.configure_fullscreen()
        self.configure_buttons()
        self.master_.after(20000, self.exit)

    def from_main_thread_nonblocking(self):
        while True:
            try:
                callback = self.callback_queue.get(False)  # doesn't block
            except Queue.Empty:  # raised when queue is empty
                break
            callback()

    def configure_buttons(self):
        self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-1.png")))
        self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-2.png")))
        self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-3.png")))
        self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-4.png")))
        self.gear_icons.append(PhotoImage(file=os.path.join("Rubik", "Assets", "gear-5.png")))

        self.button = Button(
            self.frame, text="QUIT", fg="red", command=self.exit
        )
        self.button.pack(side=LEFT)
        self.button.config(image=self.gear_icons[0])
        self.button.curr_gear = 0

        self.hi_there = Button(self.frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)
        image = PhotoImage(file=os.path.join("Rubik", "Assets", "rubik-time.png"))
        self.hi_there.config(image=image)
        self.hi_there.image = image

        self.change_gear()

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

    def change_gear(self):
        self.button.curr_gear = (self.button.curr_gear + 1) % len(self.gear_icons)
        self.button.config(image=self.gear_icons[self.button.curr_gear])
        self.gear_timer = threading.Timer(0.1, self.change_gear)
        self.gear_timer.start()

    def exit(self):
        self.gear_timer.cancel()
        self.frame.quit()
        self.master_.destroy()

    @staticmethod
    def say_hi():
        print("hi there, everyone!")

        # root = Tk()
        #
        # app = Gui(root)
        #
        # root.mainloop()
        # root.destroy()
