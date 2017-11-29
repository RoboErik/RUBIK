from Queue import *


class Command:
    def __init__(self, command, data=None, data2=None):
        self.command = command
        self.data = data
        self.data2 = data2


class QueueCommon:
    def __init__(self):
        self._command_queue = Queue()
        self._event_queue = None

    def get_queue(self):
        return self._command_queue

    def set_event_queue(self, queue):
        self._event_queue = queue

    def send_event(self, event):
        if self._event_queue is not None:
            self._event_queue.put(event)

    def check_queue(self):
        got_command = True
        while got_command:
            try:
                command = self._command_queue.get(False)
                self.handle_command(command)
                self._command_queue.task_done()
            except Empty:
                got_command = False

    def handle_command(self, command):
        raise NotImplementedError("handle_command must be implemented by the base class!")
