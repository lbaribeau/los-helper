
import threading
from threading import Thread
import atexit 

class CombatThread(threading.Thread):
    stopping = False

    def __init__(self, character, mudReaderHandler, telnetHandler, target):   
        Thread.__init__(self)
        self.character = character
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.target = target      
        numbers = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?" 
        self.it_collapsed = "Your attack overwhelms (the" + numbers + ")? (.+?) and (s?he|it) collapses!"
        self.it_fled = "(The" + numbers + " )?(.+?) flees to the (.+?)\."
        # self.regexes = ["Your attack overwhelms (the" + numbers + ")? (.+?) and (s?he|it) collapses!",
        #                 "(The" + numbers + " )?(.+?) flees to the (.+?)\."]
        self.regexes = [self.it_collapsed,
                        self.it_fled]
                #TODO: I think these groupings shouldn't include 'the'
        atexit.register(self.stop)

    def run(self):
        raise NotImplementedError("Subclasses must implement this!")

    def notify(self, regex, M_obj):
        self.stop()
        
    def stop(self):
        self.stopping = True
        self.mudReaderHandler.unregister_reaction(self)
        
    def keep_going(self):
        if self.stopping is True:
            self.stopping = False
            self.mudReaderHandler.register_reaction(self)

    def set_target(self, new_target):
        self.target = new_target

# This thread isn't getting stopped when someone in your party kills the mob...