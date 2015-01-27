
import threading
from threading import Thread
import atexit 
from misc_functions import *

class CombatThread(threading.Thread):
    stopping = False

    def __init__(self, character, mudReaderHandler, telnetHandler, target):   
        Thread.__init__(self)
        self.character = character
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.target = target
        numbers = "(\d+?1st|\d+?2nd|\d+?3rd|\d+th)" 
        #collapsed doesn't work in parties
        #self.it_collapsed = "Your attack overwhelms the (" + numbers + " )?" + target + " and (s?he|it) collapses!"
        self.enemy_defeated = "Your enemy, the (.+?) has been defeated\."
        self.it_fled = "The (" + numbers + " )?(.+?) flees to the (.+?)\."
        self.regexes = [self.enemy_defeated,
                        self.it_fled]
        atexit.register(self.stop)

    def run(self):
        raise NotImplementedError("Subclasses must implement this!")

    def notify(self, regex, M_obj):
        # magentaprint(" <" + str(self.target) + "> : " + str(self.character.MONSTER_LIST))
        # magentaprint(regex)
        if not self.stopping:
            if regex == self.enemy_defeated:
                monster = M_obj.group(1)
                if monster in self.character.MOBS_ATTACKING:
                    self.character.MOBS_ATTACKING.remove(monster)
            elif regex == self.it_fled:
                matched_groups = M_obj.groups()
                self.character.chase_mob = str(matched_groups[2])
                self.character.chase_dir = str(matched_groups[3])
            
            self.stop()
        
    def stop(self):
        if not self.stopping:
            self.stopping = True
            self.mudReaderHandler.unregister_reaction(self)
            magentaprint("Stopping '" + self.class_name() + "' thread " + self.target)
        
    def keep_going(self):
        if self.stopping is True:
            self.stopping = False
            self.mudReaderHandler.register_reaction(self)

    def set_target(self, new_target):
        self.target = new_target

    @classmethod
    def class_name(cls):  
        return cls.__name__

# This thread isn't getting stopped when someone in your party kills the mob...