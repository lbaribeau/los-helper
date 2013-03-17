
#import atexit 
import time
from CombatThread import *
from ThreadStopper import *
from misc_functions import *


class KillThread(CombatThread):
    """ This thread is used to keep time for attacks and can send an attack 
    command every few seconds.  It reads Character to determine the attack 
    period """
    def __init__(self, Character, MudReaderHandler, telnet, target):   # Constructor
        #Character, MudReaderHandler, telnet, target
        super(KillThread,self).__init__(Character, MudReaderHandler, telnet, target)
        
        # Make some ThreadStoppers.  These are BotReactions that are given to 
        # MudReaderHandler so that we can be stopped based on Mud text.
        _s_numbered = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?"
        self._reactions.append(ThreadStopper("Your attack overwhelms the" + _s_numbered + " (.+?) and (s?he|it) collapses!",self))
        self._reactions.append(ThreadStopper("The" + _s_numbered + " (.+?) flees to the (.+?)\.",self))
        
        self._reactions.append(ThreadStopper("You don't see that here\.",self))
        self._reactions.append(ThreadStopper("Attack what\?",self))
            
        #atexit.register(self.stop)

    def run(self):

        self._stopping = False
        
        self._do_reactions()
        
        wait_for_attack_ready(self.Character)

        while not self._stopping:
            self.Character.ATTACK_CLK = time.time()
            #PREV_COMMAND = "k " + self.target + "\n"
            #telnet.write(PREV_COMMAND)
            self.telnet.write("k " + self.target + "\n")
            #wait_for_attack_ready(self.Character)
            
            # OLD (deprecated by BotReactions): 
            #if(not self.MudReaderHandler.watch_attack_combat()): #TODO: delete watch_attack_combat
            #    self._stopping = True
                
            wait_for_attack_ready(self.Character)

     
    # Commenting about reactions... maybe it's better for command handler to do this
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



