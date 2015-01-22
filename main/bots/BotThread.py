import threading
from threading import Thread
import atexit 
import time
import re

from misc_functions import *
from BotReactions import GenericBotReaction
from CommandHandler import CommandHandler
from Inventory import Inventory
from Exceptions import *
from Database import *
from MudMap import MudMap

class BotThread(threading.Thread):

    def __init__(self, character, commandHandler, mudReaderHandler, inventory, mud_map):
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.__stopping = False        
        
        self.character = character
        self.commandHandler = commandHandler
        self.mudReaderHandler = mudReaderHandler
        self.inventory = inventory
        self.direction_list = []

        self.no_exit_count = 0

        self.mud_map = mud_map
        create_tables()
        db.close()

        atexit.register(self.stop)

    def stop(self):
        magentaprint("Stopping bot = " + str(self.__stopping))
        self.__stopping = True
        magentaprint("Stopping bot = " + str(self.__stopping))

    def is_stopping(self):
        return self.__stopping

    def keep_going(self):
        self.__stopping = False

    def sleep(self, duration):
        time.sleep(duration)

    def run(self):                    
        self.__stopping = False 
        self.do_run_startup()

        # Here is where the fun begins.
        while(not self.__stopping):
            if(self.__stopping):
                break

            self.do_pre_go_actions()
            
            self.direction_list = self.decide_where_to_go()
                
            while(self.direction_list != [] and not self.__stopping):
                #magentaprint(str(self.direction_list), False)
                #magentaprint("Going " + self.direction_list[0], False)
                if(self.go(self.direction_list[0])):
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
                        self.no_exit_count += 1
                        self.do_on_go_no_exit()
                        continue

                #now we add a hook for any actions in this new area    
                self.do_post_go_actions()
            self.do_after_directions_travelled()

        magentaprint("BotThread: finished now.")

    def go(self, exit_str):
        
        if(self.__stopping):
            return True
        
        wait_for_move_ready(self.character)
        wait_for_attack_ready(self.character)
        wait_for_cast_ready(self.character)

        self.character.GO_BLOCKING_MOB = ""
        self.character.GO_PLEASE_WAIT = False
        self.character.GO_NO_EXIT = False
        self.character.GO_TIMEOUT = False
        self.character.SUCCESSFUL_GO = False

        hook_found = self.do_go_hooks(exit_str)

        if not hook_found:
            if(re.match("(.*?door)", exit_str)):
                self.commandHandler.process("open " + exit_str)
                self.commandHandler.process("go " + exit_str)
            else:
                self.commandHandler.process("go " + exit_str)

            return self.check_for_successful_go()
        else:
            return hook_found

    def check_for_successful_go(self):
        return self.mudReaderHandler.check_for_successful_go()

    def do_go_hooks(self, exit_str):
        #if you want to define custom hooks like sell_items / drop_items etc... you can do so here
        return False

    def do_run_startup(self):
        #self.set_up_automatic_ring_wearing()
        #setup heal reactions
        return

    def do_pre_go_actions(self):
        self.no_exit_count = 0
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
        magentaprint("Bot: Got please wait on a go attempt, retrying.", False)

    def do_on_go_timeout(self):
        magentaprint("Bot: Check go timed out.  Could be lag.  Will try agian in 2 sec.")
        # This can happen when the system clock makes time.time() inconsistent.
        # Unless I can fix this I have to ignore this case and hope it worked.
        self.direction_list.pop(0)
        self.character.MOBS_JOINED_IN = [] 
        self.character.MOBS_ATTACKING = []
        self.sleep(2)

    def do_on_go_no_exit(self):
        # This is a tough one.  Hopefully it never 
        # happens.  I'm gonna assume it happened 
        # because the last go actually worked and 
        # was wrongly determined not to.
        magentaprint("Go no exit on: " + self.direction_list.pop(0), False)
        self.character.MOBS_JOINED_IN = []
        self.character.MOBS_ATTACKING = []

    def do_post_go_actions(self):
        #here we would implement combat or whatever other other actions we want to do before we decide where to go again
        return

    def do_after_directions_travelled(self):
        #after the direction list is empty do these things (Looking at you Goto Thread)
        return

    '''General helper functions for starting cast threads or managing inventory could be included here to assist the child classes
    The idea would be to limit the scope of the helper classes to tasks all the logic threads would need otherwise we should have
    another abstract class added'''
    def set_up_automatic_ring_wearing(self):
        """ Makes some BotReactions so that when MudReaderHandler sees us 
        pick up a ring, we'll wear it."""
        ringReaction = GenericBotReaction("(?s)You get .+? an? .+? ring((,.+?\.)|(\.))", self.commandHandler, "wear ring")
        self.mudReaderHandler.register_reaction(ringReaction)
        #Todo: fix for case where there's ring mail in the inventory or multiple rings are dropped

    def rest_and_check_aura(self):
        MANA_TO_WAIT = self.character.MAX_MANA / 2
        if self.character.BLACK_MAGIC: 
            MANA_TO_GO = self.character.MAX_MANA 
        else:
            if self.character.MAX_MANA % 2 == 1:
                MANA_TO_GO = self.character.MAX_MANA - 1 
            else:                                        
                MANA_TO_GO = self.character.MAX_MANA     
            # We just wait for an even number because all we expect to cast is vigor.

        # TODO: Keep track of when ticks are coming and how big they'll be, and avoid vigging 
        # away all the mana for characters with low piety, whose vigors will not do much, 
        # and may just be one tick away from good health. 

        aura_updated = self.update_aura()  # Most reasonable reason to fail is if we have no mana
        self.heal_up()
            
        if self.character.MANA < MANA_TO_WAIT:
            self.rest_for_mana()
        elif self.character.MANA < MANA_TO_GO:
            self.wait_for_mana()
        else:
            pass
                   
        if not aura_updated:
            self.update_aura()
    
        if True:
            self.heal_up()
            self.wait_for_mana()  
        else:
            # Probably not the greatest logic but low level characters will need 
            # to gain health other than healing up.
            self.rest_for_health()

        #self.buff_up()

        return


    def rest_for_mana(self):
        if(self.character.BLACK_MAGIC): 
            MANA_SATISFIED = self.character.MAX_MANA 
        else:
            MANA_SATISFIED = self.character.MAX_MANA - 1
        
        if(self.character.MANA < MANA_SATISFIED):
            self.commandHandler.process("rest")            

        while(self.character.MANA < MANA_SATISFIED and 
              not self.__stopping):
            
            if(self.engage_any_attacking_mobs()):
                self.commandHandler.process("rest")
                
            self.sleep(0.1)

        return


    def wait_for_mana(self):
        # Issues an enter every few seconds to get the prompt.  
        
        if(self.character.BLACK_MAGIC): 
            MANA_SATISFIED = self.character.MAX_MANA 
        else:
            MANA_SATISFIED = self.character.MAX_MANA - 1
        
        while(self.character.MANA < MANA_SATISFIED and not self.__stopping):
            self.sleep(3.5)
            self.engage_any_attacking_mobs()
            self.commandHandler.process('')
            self.sleep(1.2)  # Wait for prompt to respond before checking MANA again.
            
        return
    
    def rest_for_health(self):

        if(self.character.HEALTH >= self.character.HEALTH_TO_HEAL):
            return
            
        self.commandHandler.process("rest")            

        while(self.character.HEALTH < self.character.HEALTH_TO_HEAL and not self.__stopping):            

            if(self.engage_any_attacking_mobs()):
                self.commandHandler.process("rest")

            self.sleep(0.1)

        return


    def update_aura(self):
        if(self.__stopping):
            return False

        if(self.character.level < 1 or time.time() - self.character.AURA_LAST_UPDATE < 480):
            magentaprint("Last aura update: %d seconds ago." % round(time.time() - self.character.AURA_LAST_UPDATE))
            return True   

        wait_for_cast_ready(self.character)
        self.commandHandler.user_ca('c show')
        aura_matched = False

        while(not aura_matched and self.character.MANA > 0): 
            self.commandHandler.user_ca('c show')
            aura_matched = self.mudReaderHandler.wait_for_aura_match() 
            
        if(aura_matched):
            self.character.AURA_LAST_UPDATE = time.time()
            return True

        return False  # Ran out of mana

    
    def heal_up(self):
        magentaprint("In heal_up.")
        heal_spell = "vig"
        heal_cost = 2

        if(self.__stopping):
            return

        if self.is_character_class("Mon"):
            magentaprint("Last Meditate Check: " + str(time.time() - self.character.LAST_MEDITATE))
            if((time.time() - self.character.LAST_MEDITATE) > 150 and
                self.character.HEALTH <= self.character.HEALTH_TO_HEAL):
                self.commandHandler.process('meditate')
                self.character.LAST_MEDITATE = time.time()

        if(self.character.HEALTH <= self.character.HEALTH_TO_HEAL and 
           self.character.MANA >= heal_cost):
            if (self.character.KNOWS_VIGOR):
                self.commandHandler.user_cc(heal_spell)
        
        self.character.HAS_RESTORE_ITEMS = False

        # Just wait for MudReader to set HEALTH for us while the cast thread continues..
        while((self.character.HEALTH <= self.character.HEALTH_TO_HEAL and not self.__stopping) 
                and (self.character.MANA >= heal_cost or self.character.HAS_RESTORE_ITEMS) ):

            if (self.engage_any_attacking_mobs()):
                if(self.character.MANA >= heal_cost and self.character.KNOWS_VIGOR):
                    self.commandHandler.user_cc(heal_spell)
            
            #self.use_restorative_items() #spam them!!!

            self.sleep(0.05)

        self.commandHandler.stop_CastThread()
        
        return


    def is_character_class(self, cls):
        return self.character._class.id == cls

    def buff_up(self):
        if((time.time() - self.character.LAST_BUFF) > 180):
            #while(self.character.MANA > 0): 
                #self.commandHandler.user_ca('c light')

            self.use_buff_items()
            self.character.LAST_BUFF = time.time()
            return

    def use_buff_items(self):
        #self.commandHandler.process('drink milky')
        if (any("milky potion" in s for s in self.inventory)):
            #magentaprint("drinking steel bottle", False)
            self.commandHandler.process('drink milky')
        else:
            self.character.HAS_BUFF_ITEMS = False
        return

    def use_restorative_items(self):
        if (any("small restorative" in s for s in self.inventory)):
            magentaprint("drinking small restorative", False)
            self.commandHandler.process('drink restorative')
        else:
            self.character.HAS_RESTORE_ITEMS = False
        return

    def check_weapons(self):
        if(self.__stopping):
            return

        return

    def check_armour(self):
        if(self.__stopping):
            return

        return

    def sell_items(self):
        if(self.__stopping):
            return

        self.inventory.sell_stuff()
        
    def item_was_sold(self):
        self.character.MUD_RETURN_ITEM_SOLD = False
        self.character.SELL_CHECK_FLAG = 1
        now = time.time()

        while(self.character.SELL_CHECK_FLAG == 1 and time.time() - now < 3.0):
            self.sleep(0.05)

        magentaprint("Bot: Time for sell check was %.1f." % round(time.time()-now, 1))
        return self.character.MUD_RETURN_ITEM_SOLD    


    def drop_items(self):
        
        if(self.__stopping):
            return

        self.inventory.drop_stuff()

    def decide_which_mob_to_kill(self, monster_list):
        monster_list = monster_list[:]

        for mob in monster_list:
            if (re.search("town guard", mob) or re.search("town crier", mob) or
                re.search("clown", mob)):
                return ""

        for mob in self.character.MOBS_ATTACKING:
            if mob in monster_list:
                return mob
        
        for mob in monster_list:
            if mob in self.character.MONSTER_KILL_LIST:
                return mob
            
        return ""
    
    def engage_monster(self, monster):
        vigor_cost = 2
        black_magic_spell_cost = self.character.SPELL_COST
        
        if(self.__stopping):
            return
        
        magentaprint("Engage: " + monster)
        ifled = False

        self.commandHandler.user_kk(monster)
        self.sleep(0.5)  # Keeps attacking and magic out of sync

        while(self.commandHandler.KillThread != None and self.commandHandler.KillThread
              and self.commandHandler.KillThread.stopping == False):
            
            if(self.character.BLACK_MAGIC and self.character.MANA >= black_magic_spell_cost):
                if(self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
                    magentaprint("Starting black magic cast thread: " + monster)
                    self.commandHandler.user_cc(self.character.FAVOURITE_SPELL + " " + monster)
                else:
                    self.commandHandler.stop_CastThread()
                    
            # TODO: restoratives (use when vig not keeping up or low mana)
            if (self.character.HEALTH <= (self.character.HEALTH_TO_HEAL)):
                if self.is_character_class("Mon"):
                    magentaprint("Last Meditate Check: " + str(time.time() - self.character.LAST_MEDITATE))
                    if((time.time() - self.character.LAST_MEDITATE) > 150):
                        self.commandHandler.process('meditate')
                        self.character.LAST_MEDITATE = time.time()
                if(self.character.MANA >= vigor_cost and self.character.KNOWS_VIGOR and
                    self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
                    magentaprint("Starting vigor cast thread")
                    self.commandHandler.user_cc("vig")
                else:
                    self.commandHandler.stop_CastThread()
                #else:
                    #self.use_restorative_items()


            ifled = False
            # FLEE Checks
            if(self.character.HEALTH <= self.character.HEALTH_TO_FLEE):
                # We're done for!  Trust CommandHandler to get us out.  
                # It will turn around and stop botThread.
                self.do_flee_hook()
                ifled = True

            self.sleep(0.05)

        # OK the mob died or ran or I ran
        self.commandHandler.stop_CastThread()    
        
        if monster in self.character.MOBS_ATTACKING:
            #magentaprint("Bot:engage_monster: Removing " + monster + " from MOBS_ATTACKING.")
            magentaprint("I believe the following is dead or gone: " + monster, False)
            #check to see if "monster" we're fighting has fled
            if (not ifled):
                self.sleep(0.05)
                if monster == self.character.chase_mob:
                    self.go(self.character.chase_dir)
                    self.character.chase_mob = ""
                    self.character.chase_dir = ""
                    #append direction to movelist to follow it
                    #append direction to path back to this node
                    #execute move to target and engage
                #remove monster fled flag
            self.character.MOBS_ATTACKING.remove(monster)
            
        return

    def do_flee_hook(self):
        self.stop()  
        self.commandHandler.user_flee() 

    def get_items(self):
        if(self.__stopping):
            return

        self.commandHandler.process("ga")  
        return

    def engage_mobs_who_joined_in(self):
        while(self.character.MOBS_JOINED_IN != []):
            self.engage_monster(self.character.MOBS_JOINED_IN[0])
            self.character.MOBS_JOINED_IN = self.character.MOBS_JOINED_IN[1:]
            self.get_items()         

        return
    
    def engage_any_attacking_mobs(self):
        engaged = False

        while(self.character.MOBS_ATTACKING != []):
            engaged = True
            self.engage_monster(self.character.MOBS_ATTACKING[0])
            self.get_items()

        return engaged
    
    def ready_for_combat(self):
        return (self.character.HEALTH > self.character.HEALTH_TO_HEAL and
                self.character.MANA >= self.character.MANA_TO_ENGAGE)