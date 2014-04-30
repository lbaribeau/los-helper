
import threading
from threading import Thread
import atexit 
import time

from misc_functions import *
from CommandHandler import *
from Inventory import *
from Exceptions import *

class LogicThread(threading.Thread):

    def __init__(self, starting_path=None, character_in=None, commandHandler=None, 
                 mudReaderHandler_in=None, inventory_in=None):
        if(starting_path==None and character_in==None and commandHandler==None 
           and mudReaderHandler_in==None and inventory_in==None):
            return   
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.__stopping = False        
        
        self.character = character_in
        self.commandHandler = commandHandler
        self.mudReaderHandler = mudReaderHandler_in
        self.inventory = inventory_in
        self.direction_list = []


    def stop(self):
        magentaprint("Stopping bot.", False)
        self.__stopping = True


    def keep_going(self):
        self.__stopping = False

    def run(self):                    
        self.__stopping = False 
        
        magentaprint("BotThread: run()")

        self.do_run_startup()

        # Here is where the fun begins.
        while(not self.__stopping):
            if(self.__stopping):
                break

            self.do_pre_go_actions()
            
            self.decide_where_to_go()
                
            while(direction_list != [] and not self.__stopping):
                if(self.go(direction_list[0])):
                    # Successful go.
                    self.do_on_succesful_go()
                else:
                    if(self.character.GO_BLOCKING_MOB != ""):
                        # MUDReaderThread sets GO_BLOCKING_MOB when go returns false
                        self.do_on_blocking_mob()
                        continue

                    elif(self.character.GO_PLEASE_WAIT):
                        # Just try again.
                        self.do_on_go_please_wait()
                        continue
                    elif(self.character.GO_TIMEOUT):
                        self.do_on_go_timeout()
                    elif(self.character.GO_NO_EXIT): 
                        self.do_on_go_no_exit()
                        continue

                #now we add a hook for any actions in this new area    
                self.do_post_go_actions()

        magentaprint("BotThread: finished now.")

    def go(self, exit_str):
        
        if(self.__stopping):
            return True
        
        magentaprint("Going " + exit_str + (". %f" % (time.time() - self.character.START_TIME)))
        wait_for_move_ready(self.character)
        wait_for_attack_ready(self.character)
        wait_for_cast_ready(self.character)

        if(exit_str == "nw" or exit_str == "ne" or
           exit_str == "sw" or exit_str == "se" or
           exit_str == 'n' or exit_str == 'e' or
           exit_str == 's' or exit_str == 'w'):
            self.commandHandler.process(exit_str)
            return self.mudReaderHandler.check_for_successful_go() 

        '''elif(re.match("open ", exit_str)):
            self.commandHandler.process(exit_str)
            self.commandHandler.process("go " + exit_str.split(' ')[1])
            return self.mudReaderHandler.check_for_successful_go() 

        elif(exit_str == "prepare"):
            self.commandHandler.process(exit_str)
            return True

        elif(exit_str == "sell_items"):
            self.sell_items()
            return True

        elif(exit_str == "drop_items"):
            self.drop_items()
            return True'''

        else:
            self.commandHandler.process("go " + exit_str)
            return self.mudReaderHandler.check_for_successful_go()

    def do_run_startup(self):
        #self.set_up_automatic_ring_wearing()
        #setup heal reactions
        return

    def do_pre_go_actions(self):
        #self.rest_and_check_aura()
        #self.check_weapons()
        #self.check_armour()
        return         

    def decide_where_to_go(self): #each logic thread will have to implement this function
        #self.directionlist = []
        raise NotImplementedError()

    def do_on_succesful_go(self):
        self.direction_list.pop(0)
        self.character.MOBS_JOINED_IN = [] 
        self.character.MOBS_ATTACKING = []
        return

    def do_on_blocking_mob(self):
        #self.engage_monster(self.character.GO_BLOCKING_MOB)
        #self.get_items()
        #self.character.GO_BLOCKING_MOB = ""
        #self.engage_mobs_who_joined_in()
        #self.engage_any_attacking_mobs()
        #self.check_weapons()
        
        #if (not self.character.BLACK_MAGIC):
        #    self.heal_up()
        return

    def do_on_go_please_wait(self):
        magentaprint("Bot: Got please wait on a go attempt, retrying.")

    def do_on_go_timeout(self):
        magentaprint("Bot: Check go timed out.  Could be lag.  Will try agian in 2 sec.")
        # This can happen when the system clock makes time.time() inconsistent.
        # Unless I can fix this I have to ignore this case and hope it worked.
        self.direction_list.pop(0)
        self.character.MOBS_JOINED_IN = [] 
        self.character.MOBS_ATTACKING = []
        time.sleep(2)

    def do_on_go_no_exit(self):
        # This is a tough one.  Hopefully it never 
        # happens.  I'm gonna assume it happened 
        # because the last go actually worked and 
        # was wrongly determined not to.
        self.direction_list.pop()
        self.character.MOBS_JOINED_IN = []
        self.character.MOBS_ATTACKING = []

    def do_post_go_actions():
        #here we would implement combat or whatever other other actions we want to do before we decide where to go again
        return

    '''General helper functions for starting cast threads or managing inventory could be included here to assist the child classes
    The idea would be to limit the scope of the helper classes to tasks all the logic threads would need otherwise we should have
    another abstract class added'''
