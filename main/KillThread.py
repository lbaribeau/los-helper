
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
        super(KillThread,self).__init__(Character, MudReaderHandler, telnet, target)
        
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
            #self.telnet.write("k " + self.target + "\n")
            send_to_telnet(self.telnet, "k " + self.target)
            #wait_for_attack_ready(self.Character)
            
            # OLD (deprecated by BotReactions): 
            #if(not self.MudReaderHandler.watch_attack_combat()): #TODO: delete watch_attack_combat
            #    self._stopping = True     
            wait_for_attack_ready(self.Character)

        self._undo_reactions()
        # end thread

     
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

    # Why use a ThreadKiller - just implement notify() on the Threads.  Because there 
    # are multiple regexes.  TODO: I think that changing BotReactions to use a list of regexes, 
    # and having CombatThread inherit BotReactions could deprecate ThreadStopper. 
