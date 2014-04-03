
from misc_functions import *
import threading
from threading import Thread
import atexit 
import time
#from BotReaction import BotReaction

# class CoolAbilityThread(threading.Thread, BotReaction):
class CoolAbilityThread(threading.Thread):
    # This thread is used to time retries for cool abilities (haste, pray, berserk, etc.).  
    # Construct it with a CoolAbility.
    # (Not taking Character in - shouldn't be necessary)
    def __init__(self, CoolAbility, MudReaderHandler, tn_in):   # Constructor
        Thread.__init__(self)
        
        # Input objects
        self.CoolAbility = CoolAbility # Not doing _inst notation
        self.MudReaderHandler = MudReaderHandler

        # BotReaction stuff
        #super(BotReaction, self).__init__(CoolAbility.) #TODO
          # Use a reaction for success_mud_text and one for failure_mud_text

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

            self.MudReaderHandler.register_reaction(self)

            if(self.CoolAbility.needs_target()):
                #self.tn.write(self.CoolAbility.command() + " " + self.target + "\n")
                send_to_telnet(self.tn, self.CoolAbility.command() + " " + self.target)
            else:
                #self.tn.write(self.CoolAbility.command() + "\n")
                send_to_telnet(self.tn, self.CoolAbility.command())

    def notify(self, M_obj):

        self.MudReaderHandler.unregister_reaction(self)
        self.stop()

            # if(self.CoolAbility.needs_target()):
            #     self.tn.write(self.CoolAbility.command() + " " + self.target + "\n")
            # else:
            #     self.tn.write(self.CoolAbility.command() + "\n")

            # # if(self.mudreaderhandler.wait_for_ability_feedback(coolability)):
            # # if(self.mudreaderhandler.do_whole_command(coolability.)):
            # success = self.mudreaderhandler.wait_for_feedback(coolability.success_mud_text(), coolability.failure_mud_text)

            # if(success):
            #     #success.  go to sleep and notify when cooldown is back up.
            #     time.sleep(max(0,
            #         self.coolability.success_cooldown() - (time.time() - self.__clock)))
            #     magentaprint("--- " + coolability.command() + " cooldown is up!")
            #     self.stop()
            # else:
            #     #fail.  wait cooldown then let loop reiterate. 
            #     # todo: be robust for "please wait one second."
            #     time.sleep(max(0,
            #         self.CoolAbility.failure_cooldown() - (time.time() - self.__CLOCK)))
               
    #         # (Thinking comments:)     
    #         # I think I need to use MudReaderHandler to determine whether 
    #         # this worked or not.  If it worked I should wait Cooldown and then print
    #         # a message saying when the cooldown's up, and if it didn't work I should 
    #         # iterate again after CooldownFail.  If not using MudReaderHandler, I could 
    #         # just have MudReaderThread hit this thread, but I think the flags 
    #         # method is better. 
    #         # PLAN: Implement CoolAbility thread in this way now and rewrite CastThread
    #         # and KillThread to use flags.  Generally, have the threads use the MudReader 
    #         # instead of the other way around.
            
    #         # TODO: I will need two instances of this thread for classes with two 
    #         # CoolAbilities(like paladin's pray / turn or antipaladin's berserk / wither)  
    #         # This logic is owned by CommandHandler.  

    # def run(self):
    #     self.__stopping = False
        # while not self.__stiopping:
        #     self.__CLOCK = time.time()

        #     if (! self.CoolAbility.needsTarget):
        #         success = self.MudReaderHandler.do_whole_command(
        #             self.CoolAbility.command(),
        #             self.CoolAbility.success_mud_text(),
        #             self.CoolAbility.failure_mud_text())
        #     else:
        #         success = self.MudReaderHandler.do_whole_command(
        #             self.CoolAbility.command() + " " + self.target,
        #             self.CoolAbility.success_mud_text(),
        #             self.CoolAbility.failure_mud_text())

        #     if (success):
        #         # Go to sleep and notify when cooldown is back up
        #         time.sleep(max(0,
        #             self.CoolAbility.success_cooldown() - (time.time() - self.__CLOCK)))
        #         magentaprint("--- " + CoolAbility.command() + " cooldown is up!");
        #         self.stop()
        #     else:
        #         # Wait cooldown and try again after
        #         # TODO: Be robust for "Please wait one second."
        #         time.sleep(max(0,
        #             self.CoolAbility.failure_cooldown() - (time.time() - self.__CLOCK)))
                
                           
            


