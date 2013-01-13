
from misc_functions import *
import threading
from threading import Thread
import atexit 
import time

class KillThread(threading.Thread):
    # This thread keeps attacking time in combat.  There is only one instance
    # of it in the program and it is global.  It can be stopped with the
    # stop function.  
    def __init__(self, Character_inst_in, MudReaderHandler_in, tn_in, target):   # Constructor
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.__stopping = False
        self.Character_inst = Character_inst_in
        self.MudReaderHandler = MudReaderHandler_in
        self.tn = tn_in
        self.target = target      # the string argument indicating the target.
        if(self.Character_inst.HASTING):
            self.delay = self.Character_inst.ATTACK_PERIOD_HASTE
        else:
            self.delay = self.Character_inst.ATTACK_PERIOD
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
    
    def set_delay(self, new_delay):     # NOT USED AT ALL!!!
        # Used if haste is gained or lost in combat.  # NOT ANYMORE!                               
        self.delay = new_delay

    def run(self):
        # Called by start().  Need to add a parameter argv.  Didn't work.
        # However delay is automatic (in constructor)
        # Assumption is that it is constructed and started at the same time.

        self.__stopping = False
        wait_for_attack_ready(self.Character_inst)
        while not self.__stopping:
            self.Character_inst.ATTACK_CLK = time.time()
            #PREV_COMMAND = "k " + self.target + "\n"
            #tn.write(PREV_COMMAND)
            self.tn.write("k " + self.target + "\n")
            #wait_for_attack_ready(self.Character_inst)
            
            # Nov2012.  Maybe what needs to happen here is that I need to ask MudReader to check if the monster died, and stop if so.
            # Also, check if I got updated during the wait.
            if(not self.MudReaderHandler.watch_attack_combat()):
                self.__stopping = True
            wait_for_attack_ready(self.Character_inst)
            

        



