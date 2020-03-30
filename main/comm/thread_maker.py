
from threading import Thread

class ThreadMaker(Thread):
    # Allows starting a bot thread that uses a function other than 'run'
    # So I don't have to make a new class for every threaded operation

    def __init__(self, t, t_function_name):
        super().__init__()
        self.t = t
        self.t_function_name = t_function_name

    def stop(self):
        self.t.stop()

    def run(self):
        getattr(self.t, self.t_function_name)()  # TODO - call a function knowing the name
