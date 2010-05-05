
from misc_functions import *
import threading
from threading import Thread
import atexit 
import time

class CastThread(threading.Thread):
    # This thread keeps casting time in combat.  There is only one instance
    # of it in the program and it is global.  It can be stopped with the
    # stop function.
    # TBD: Watch for failed casts?  Recast? 
    def __init__(self, Character_inst_in, tn_in, spell, target):   # Constructor
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.__stopping = False
        self.Character_inst = Character_inst_in
        self.tn = tn_in
        self.spell = spell
        self.target = target
        # Is there a cast haste?
        self.delay = self.Character_inst.CAST_PERIOD        
        atexit.register(self.stop)

    def stop(self):
        self.__stopping = True

    def keep_going(self):
        self.__stopping = False

    def set_target(self, new_target):
        # Used if target is changed in combat
        self.target = new_target

    def set_spell(self, new_spell):
        # Used if spell is changed in combat
        self.spell = new_spell
    
    def set_delay(self, new_delay): # NOT EFFECTIVE
        # I don't think I ever use this
        self.delay = new_delay

    def run(self):
        # Called by start().  Need to add a parameter argv.  EDIT: Didn't work.
        # However delay is automatic (in constructor)
        # Assumption is that it is constructed and started at the same time.

        self.__stopping = False
        wait_for_cast_ready(self.Character_inst)
        while not self.__stopping:
            # TBD: Monitor current spell and current mana and stop if out
            # of mana.
            self.Character_inst.CAST_CLK = time.time()
            #PREV_COMMAND = "cast " + self.spell + " " + self.target + "\n"
            #tn.write(PREV_COMMAND)
            self.tn.write("cast " + self.spell + " " + self.target + "\n")
            wait_for_cast_ready(self.Character_inst)




