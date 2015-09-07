
from threading import Thread

from misc_functions import magentaprint

class ThreadingMixin(object):
    # SmartCombat, Kill, and Cast
    # (Well, not SmartCombat...)
    # target = None  
    thread = None
    stopping = False
      
    @classmethod
    def stop(cls):
        cls.stopping = True

    @classmethod
    def keep_going(cls):
        magentaprint(str(cls) + " keep_going " + str(cls.stopping))
        
        if cls.stopping is True:
            cls.stopping = False

    @classmethod
    def spam(cls, telnetHandler, target=None):
        cls.stopping = False
        cls.target = target

        if cls.thread is None or not cls.thread.is_alive():
            # not is_alive() means it won't look at stopping anymore so we're good.
            cls.thread = Thread(target = cls.run, args = (telnetHandler, target))
            cls.thread.daemon = True
            cls.thread.start()
        # else:
            # Well the other thread CAN stil be sleeping from a kill error.  (ie misspelled target)
            # That puts it into a 3 second sleep, then the timer gets corrected 0.3s after.
            # So.... maybe it must poll fast... or we need signals... do we use that thread or a new thread??
            # Maybe we write its code smarter to handle this case... don't sleep till after the cooldown's verified

    def start_thread(self, target=None):
        self.spam(self.telnetHandler, target)

