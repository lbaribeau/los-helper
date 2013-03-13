
from misc_functions import *
import threading
from threading import Thread
import atexit 
import time

class CastThread(threading.Thread):
    """ This thread is used to keep time for casts and can send a cast  
    command every DELAY seconds """
    # TODO: Watch for failed casts?  Recast? 
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
        
        # Make some ThreadStoppers.  These are BotReactions that are given to 
        # MudReaderHandler so that we can be stopped based on Mud text.
        # TODO
        #self._reactions = []
        #_s_numbered = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?"
        #self._reactions.append(ThreadStopper("Your attack overwhelms the" + _s_numbered + " (.+?) and (s?he|it) collapses!",self))
        #self._reactions.append(ThreadStopper("The" + _s_numbered + " (.+?) flees to the (.+?)\.",self))
        #self._reactions.append(ThreadStopper("You don't see that here\.",self))
        #self._reactions.append(ThreadStopper("Attack what\?",self))    
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
            # TODO: Monitor current spell and current mana and stop if out
            # of mana.
            self.Character_inst.CAST_CLK = time.time()
            #PREV_COMMAND = "cast " + self.spell + " " + self.target + "\n"
            #tn.write(PREV_COMMAND)
            self.tn.write("cast " + self.spell + " " + self.target + "\n")
            wait_for_cast_ready(self.Character_inst)




