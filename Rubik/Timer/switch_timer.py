import time
from .. import utils


# Counts the time between a switch being released and pressed again. The timer
# will continue to count from the first time on_switch_up is called until
# reset() is called.
class SwitchTimer:

    start_time = -1
    end_time = -1
    elapsed_time = -1

    def on_switch_up(self):
        if self.start_time == -1:
            self.start_time = utils.milli_time()

    def reset(self):
        self.start_time = -1
        self.end_time = -1

    def on_switch_down(self):
        self.end_time = utils.milli_time()
        self.elapsed_time = self.end_time - self.start_time
        return self.elapsed_time