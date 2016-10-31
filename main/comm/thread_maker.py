
from threading import Thread
from misc_functions import magentaprint

class ThreadMaker(Thread):
    # Allows starting a bot thread that uses a function other than 'run'
    # So I don't have to make a new class for every threaded operation
    # (I do have to make a new ThreadMaker for each new thread.  This makes a thread out of any function.)
    # In order to support stop(), I will need a new object each time!  And not a ThreadMaker object!  (the called
    # function has to check self.stop() and exit cleanly...)  Well how about sending a stop signal??


    def __init__(self, t, t_function_name):
        super().__init__()
        self.t = t
        self.t_function_name = t_function_name

    def stop(self):
        magentaprint("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ThreadMaker.stop()")
        self.t.stop()

    def run(self):
        getattr(self.t, self.t_function_name)()  # TODO - call a function knowing the name

    # def is_alive(self):
    #     return self.t.is_alive()  # It should inherit this from Thread

    def stopping(self):
        return self.t.stopping
