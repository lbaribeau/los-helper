
from threading import Thread

from misc_functions import magentaprint

class ThreadingMixin:
# class ThreadingMixin(Thread):
    # SmartCombat, Kill, and Cast
    # (Well, not SmartCombat...)
    # target = None  

    thread = None
    stopping = False
      
    #@classmethod
    def stop(self):
        self.stopping = True

    #@classmethod
    def keep_going(cls):
        magentaprint(str(cls) + " keep_going; (stopping was " + str(cls.stopping)+")")
        cls.stopping = False

    # #@classmethod
    # def spam(cls, telnetHandler, target=None):
    #     cls.stopping = False
    #     cls.target = target

    #     if cls.thread is None or not cls.thread.is_alive():
    #         # not is_alive() means it won't look at stopping anymore so we're good.
    #         #cls.thread = Thread(target=cls.run, args=(telnetHandler, target))
    #         cls.thread.daemon = True # the program will exit even if this thread is still alive
    #         cls.thread.start()
    #     # else:
    #         # Well the other thread CAN stil be sleeping from a kill error.  (ie misspelled target)
    #         # That puts it into a 3 second sleep, then the timer gets corrected 0.3s after.
    #         # So.... maybe it must poll fast... or we need signals... do we use that thread or a new thread??
    #         # Maybe we write its code smarter to handle this case... don't sleep till after the cooldown's verified

    def spam(self, telnetHandler, target=None):
        self.stopping = False
        self.target = target # to send the command (thread target function is called _target)

        if self.thread is None or not self.thread.is_alive():
            # not is_alive() means it won't look at stopping anymore so we're good.
            #cls.thread = Thread(target=cls.run, args=(telnetHandler, target))
            self.thread = Thread(target=self.run, args=(telnetHandler, target)) 
            # One target is the thread target function
            # The other target is from the telnet command string
            self.thread.daemon = True # the program will exit even if this thread is still alive
            self.thread.start()
        # else:
            # Well the other thread CAN stil be sleeping from a kill error.  (ie misspelled target)
            # That puts it into a 3 second sleep, then the timer gets corrected 0.3s after.
            # So.... maybe it must poll fast... or we need signals... do we use that thread or a new thread??
            # Maybe we write its code smarter to handle this case... don't sleep till after the cooldown's verified

    def start_thread(self, target=None):
        self.spam(self.telnetHandler, target)


    # Expect run to be defined by child
    # We aren't inheriting Thread, we are making a thread by giving self.run

