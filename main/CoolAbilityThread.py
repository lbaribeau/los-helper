
from misc_functions import *
import threading
from threading import Thread
import atexit 
import time

class CoolAbilityThread(threading.Thread):
    # This thread is used to time retries for cool abilities (haste, pray, berserk, etc.).  
    # Construct it with a CoolAbility.
    # (Not taking Character in - shouldn't be necessary)
    def __init__(self, CoolAbility, MudReaderHandler, tn_in):   # Constructor
        Thread.__init__(self)
        
        # Input objects
        self.CoolAbility=CoolAbility # Not doing _inst notation
        self.MudReaderHandler=MudReaderHandler
        # Initialize some variables local to this thread
        self.__stopping = False
        self.__CLOCK = -CoolAbility.getCoolDownInSecondsAfterSuccess()
        self.tn = tn_in
        self.target = target      
        atexit.register(self.stop)

    def stop(self):
        self.__stopping = True

    def keep_going(self):
        self.__stopping = False

    def get_stopping(self):
        return self.__stopping

    def set_target(self, new_target):
        # Used if target is changed in combat
        self.target = new_target
        
    def get_timer(self):
        return time.time() - self.__CLOCK
    
    def run(self):
        self.__stopping = False
        while not self.__stopping:
            self.__CLOCK = time.time()
            if(self.CoolAbility.getNeedsTarget()):
                self.tn.write(self.CoolAbility.getCommand() + " " + self.target + "\n")
            else:
                self.tn.write(self.CoolAbility.getCommand() + "\n")
            if(self.MudReaderHandler.wait_for_ability_feedback(CoolAbility)):
                #Success.  Go to sleep and notify when cooldown is back up.
                time.sleep(max(0,
                    self.CoolAbility.getSuccessCooldown() - (time.time() - self.__CLOCK)))
                magentaprint(CoolAbility.getCommand() + " cooldown is up!")
                self.stop()
            else:
                #Fail.  Wait cooldown then let loop reiterate. 
                # TODO: Be robust for "Please wait one second."
                time.sleep(max(0,
                    self.CoolAbility.getFailureCooldown() - (time.time() - self.__CLOCK)))
               
            # (Thinking comments:)     
            # I think I need to use MudReaderHandler to determine whether 
            # this worked or not.  If it worked I should wait Cooldown and then print
            # a message saying when the cooldown's up, and if it didn't work I should 
            # iterate again after CooldownFail.  If not using MudReaderHandler, I could 
            # just have MudReaderThread hit this thread, but I think the flags 
            # method is better. 
            # PLAN: Implement CoolAbility thread in this way now and rewrite CastThread
            # and KillThread to use flags.  Generally, have the threads use the MudReader 
            # instead of the other way around.
            
            # TODO: I will need two instances of this thread for classes with two 
            # CoolAbilities(like paladin's pray / turn or antipaladin's berserk / wither)  
            # This logic is owned by CommandHandler.  

                
                           
            


