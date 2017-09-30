from tkinter import *
import os, time, threading


class Gui():
    master_ = None
    gear_icons = []
    gear_timer = None

    def __init__(self, master):
        super().__init__()
        self.master_ = master
        self.frame = Frame(master)
        self.frame.pack()

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

    def change_gear(self):
        self.button.curr_gear = (self.button.curr_gear + 1) % len(self.gear_icons)
        self.button.config(image=self.gear_icons[self.button.curr_gear])
        self.gear_timer = threading.Timer(0.1, self.change_gear)
        self.gear_timer.start()

    def exit(self):
        self.gear_timer.cancel()
        self.frame.quit()

    @staticmethod
    def say_hi():
        print("hi there, everyone!")

        # root = Tk()
        #
        # app = Gui(root)
        #
        # root.mainloop()
        # root.destroy()
