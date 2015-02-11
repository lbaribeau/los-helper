
import threading
from threading import Thread
import atexit 

from misc_functions import magentaprint

class CombatThread(threading.Thread):

    def __init__(self, character, mudReaderHandler, telnetHandler, target):   
        Thread.__init__(self)
        self.stopping = False
        self.character = character
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.target = target      
        numbers = "(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th|16th|17th|18th|19th)" 
        self.it_collapsed = "Your attack overwhelms the (" + numbers + " )?(.+?) and (s?he|it) collapses!"
        self.it_fled = "The (" + numbers + " )?(.+?) flees to the (.+?)\."
        self.regexes = [self.it_collapsed,
                        self.it_fled]
        # atexit.register(self.stop)

    def notify(self, regex, M_obj):
        magentaprint(str(self) + " notified.")
        self.stop()
        
    def stop(self):
        self.stopping = True

    def end_run(self):
        self.unregistered = True
        magentaprint(str(self) + " ended run.")

    def keep_going(self):
        magentaprint(str(self) + " keep_going " + str(self.stopping))
        
        if self.stopping is True:
            self.stopping = False

    def set_target(self, new_target):
        self.target = new_target

# This thread isn't getting stopped when someone in your party kills the mob...