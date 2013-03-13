
from misc_functions import *
import threading
from threading import Thread
import atexit 
import time
from ThreadStopper import *

class KillThread(threading.Thread):
    """ This thread is used to keep time for attacks and can send an attack 
    command every DELAY seconds """
    def __init__(self, Character, MudReaderHandler, telnet, target):   # Constructor
        Thread.__init__(self)
        self.__stopping = False
        self.Character = Character
        self.MudReaderHandler = MudReaderHandler
        self.telnet = telnet
        self.target = target      # the string argument indicating the target.
        
        # Make some ThreadStoppers.  These are BotReactions that are given to 
        # MudReaderHandler so that we can be stopped based on Mud text.
        self._reactions = []
        _s_numbered = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?"
        self._reactions.append(ThreadStopper("Your attack overwhelms the" + _s_numbered + " (.+?) and (s?he|it) collapses!",self))
        self._reactions.append(ThreadStopper("The" + _s_numbered + " (.+?) flees to the (.+?)\.",self))
        self._reactions.append(ThreadStopper("You don't see that here\.",self))
        self._reactions.append(ThreadStopper("Attack what\?",self))
        if(self.Character.HASTING):
            self.delay = self.Character.ATTACK_PERIOD_HASTE
        else:
            self.delay = self.Character.ATTACK_PERIOD
        atexit.register(self.stop)

    def stop(self):
        self.__stopping = True
        self._undo_reactions()

    def keep_going(self):
        if(self.__stopping == True):
            self.__stopping = False
            self._do_reactions()

    def get_stopping(self):
        return self.__stopping

    def set_target(self, new_target):
        # Used if target is changed in combat
        self.target = new_target
    
    def set_delay(self, new_delay):
        # May be used if haste is gained or lost in combat.  
        # Not currently being used                            
        self.delay = new_delay

    def run(self):
        # Called by start().  Need to add a parameter argv.  Didn't work.
        # However delay is automatic (in constructor)
        # Assumption is that it is constructed and started at the same time.

        self.__stopping = False
        
        self._do_reactions()
        
        wait_for_attack_ready(self.Character)

        while not self.__stopping:
            self.Character.ATTACK_CLK = time.time()
            #PREV_COMMAND = "k " + self.target + "\n"
            #telnet.write(PREV_COMMAND)
            self.telnet.write("k " + self.target + "\n")
            #wait_for_attack_ready(self.Character)
            
            # OLD (deprecated by BotReactions): 
            #if(not self.MudReaderHandler.watch_attack_combat()): #TODO: delete watch_attack_combat
            #    self.__stopping = True
                
            wait_for_attack_ready(self.Character)

    def _do_reactions(self):
        """ Makes and registers threadstoppers for a killthread """
        for reaction in self._reactions:
            self.MudReaderHandler.register_reaction(reaction)
    
    def _undo_reactions(self):
        for reaction in self._reactions:
            self.MudReaderHandler.unregister_reaction(reaction)
     
    # Commenting... maybe it's better for command handler to do this
    # Command handler needs to make a couple of stopper objects.
    # The reason why is that there needs to be more than one regex that can stop us.
    # CommandHandler must do it because I don't want to make child objects that 
    # can stop the parent.  Well... I could make those objects here... the problem 
    # with having command handler do it is that someone has to keep track of 
    # registering and unregistering the stopper objects, and that may as well be done
    # here, because it's the best way to make sure they get unregistered everytime I'm 
    # stopped.  Should I really have access to MudReaderThread though?  I think so...
    # I think that's the org I want - MudReader should get used and not use.  So, try that 
    # next.. have Kill make its own stoppers and register/unregister them.



