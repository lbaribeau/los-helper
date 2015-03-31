
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

    def __init__(self, character, commandHandler, mudReaderHandler, database, mud_map):
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.stopping = False        
        
        self.character = character
        self.commandHandler = commandHandler
        self.mudReaderHandler = mudReaderHandler
        self.inventory = character.inventory
        self.smartCombat = commandHandler.smartCombat
        self.kill = self.smartCombat.kill
        self.cast = self.smartCombat.cast
        self.direction_list = []

        self.database = database
        db.initialize(database)
        db.connect()
        self.mud_map = mud_map
        create_tables()
        db.close()

        atexit.register(self.stop)

    def stop(self):
        magentaprint("Stopping bot.")
        self.stopping = True

    def is_stopping(self):
        return self.stopping

    def keep_going(self):
        self.stopping = False

    def run(self):                    
        self.stopping = False 
        self.do_run_startup()

        # Here is where the fun begins.
        while not self.stopping:

            self.do_pre_go_actions()

            if self.stopping:
                break
            
            self.direction_list = self.decide_where_to_go()
                
            while self.direction_list != [] and not self.stopping:
                if self.go(self.direction_list[0]):
                    # Successful go.
                    self.do_on_succesful_go()
                else:
                    if self.character.GO_BLOCKING_MOB != "":
                        # MUDReaderThread sets GO_BLOCKING_MOB when go returns false
                        self.do_on_blocking_mob()
                        continue

                    elif self.character.GO_PLEASE_WAIT:
                        # Just try again.
                        self.do_on_go_please_wait()
                        continue
                    elif self.character.GO_TIMEOUT:
                        self.do_on_go_timeout()
                    elif self.character.GO_NO_EXIT: 
                        self.do_on_go_no_exit()
                        continue

                #now we add a hook for any actions in this new area    
                self.do_post_go_actions()
            self.do_after_directions_travelled()

        magentaprint("BotThread: finished now.")

    def go(self, exit_str):
        
        if(self.stopping):
            return True
        
        wait_for_move_ready(self.character)
        self.kill.wait_until_ready()
        self.cast.wait_until_ready()
        magentaprint("Going " + exit_str + (". %.1f" % (time.time() - self.character.START_TIME)))

        if(re.match("(.*?door)", exit_str)):
            self.commandHandler.process("open " + exit_str)
            self.commandHandler.process("go " + exit_str)
            return self.mudReaderHandler.check_for_successful_go()
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
        magentaprint("Bot: Check go timed out.  Could be lag.  Will try again in 8 sec.")
        # This can happen when the system clock makes time.time() inconsistent.
        # Unless I can fix this I have to ignore this case and hope it worked.
        self.direction_list.pop(0)
        self.character.MOBS_JOINED_IN = [] 
        self.character.MOBS_ATTACKING = []
        time.sleep(8)

    def do_on_go_no_exit(self):
        # This is a tough one.  Hopefully it never 
        # happens.  I'm gonna assume it happened 
        # because the last go actually worked and 
        # was wrongly determined not to.
        self.direction_list.pop()
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
        """ Makes a BotReaction so that when MudReaderHandler sees us 
        pick up a ring, we'll wear it."""
        ringReaction = GenericBotReaction("(?s)You get .+? an? .+? ring((,.+?\.)|(\.))", self.commandHandler, "wear ring")
        self.mudReaderHandler.register_reaction(ringReaction)
        #Todo: fix for case where there's ring mail in the inventory or multiple rings are dropped

    def rest_and_check_aura(self):
        MANA_TO_WAIT = self.character.MAX_MANA - 12
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
    
        if self.character.level > 3:
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
              not self.stopping):
            
            if(self.engage_any_attacking_mobs()):
                self.commandHandler.process("rest")
                
            time.sleep(0.1)

        return


    def wait_for_mana(self):
        # Issues an enter every few seconds to get the prompt.  
        
        if(self.character.BLACK_MAGIC): 
            MANA_SATISFIED = self.character.MAX_MANA 
        else:
            MANA_SATISFIED = self.character.MAX_MANA - 1
        
        while(self.character.MANA < MANA_SATISFIED and not self.stopping):
            time.sleep(3.0)
            self.engage_any_attacking_mobs()
            self.commandHandler.process('')
            time.sleep(1.2)  # Wait for prompt to respond before checking MANA again.
            
        return
    
    def rest_for_health(self):

        if(self.character.HEALTH >= self.character.HEALTH_TO_HEAL):
            return
            
        self.commandHandler.process("rest")            

        while(self.character.HEALTH < self.character.HEALTH_TO_HEAL and not self.stopping):            

            if(self.engage_any_attacking_mobs()):
                self.commandHandler.process("rest")

            time.sleep(0.1)

        return


    def update_aura(self):
        # This could be written
        # - put aura variables in Cast not character
        # - only use Command type structures and delete a lot of code from MudReaderHandler
        # - write a 'execute_until_success' function into command

        if self.stopping:
            return False

        if self.character.level < 3 or time.time() - self.character.AURA_LAST_UPDATE < 480:
            magentaprint("Last aura update: %d seconds ago." % round(time.time() - self.character.AURA_LAST_UPDATE))
            return True   

        self.cast.wait_until_ready()
        aura_matched = False

        while(not aura_matched and self.character.MANA > 0): 
            self.cast.cast('show')
            # self.cast.wait_for_flag()
            aura_matched = self.mudReaderHandler.wait_for_aura_match() 
            
        if(aura_matched):
            self.character.AURA_LAST_UPDATE = time.time()
            return True

        return False  # Ran out of mana

    
    def heal_up(self):
        heal_spell = "vig"
        heal_cost = 2

        if(self.stopping):
            return

        if (self.character._class.id == "Mon"):
            magentaprint("Last Meditate Check: " + str(time.time() - self.character.LAST_MEDITATE))
            if((time.time() - self.character.LAST_MEDITATE) > 150 and
                self.character.HEALTH <= self.character.HEALTH_TO_HEAL):
                self.commandHandler.process('meditate')
                self.character.LAST_MEDITATE = time.time()

        if(self.character.HEALTH <= self.character.HEALTH_TO_HEAL and 
           self.character.MANA >= heal_cost):
            if (self.character.KNOWS_VIGOR):
                # self.commandHandler.user_cc(heal_spell)
                self.cast.__class__.command = 'cas vig'
                self.cast.start_thread()
        
        self.character.HAS_RESTORE_ITEMS = False

        # Just wait for MudReader to set HEALTH for us while the cast thread continues..
        while((self.character.HEALTH <= self.character.HEALTH_TO_HEAL and not self.stopping) 
                and (self.character.MANA >= heal_cost or self.character.HAS_RESTORE_ITEMS) ):

            if (self.engage_any_attacking_mobs()):
                if(self.character.MANA >= heal_cost and self.character.KNOWS_VIGOR):
                    # self.commandHandler.user_cc(heal_spell)
                    self.cast.__class__.command = 'cas vig'
                    self.cast.start_thread()
            
            #self.use_restorative_items() #spam them!!!

            time.sleep(0.05)

        # self.commandHandler.stop_CastThread()
        self.cast.stop()
        
        return

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
        if(self.stopping):
            return

        return

    def check_armour(self):
        if(self.stopping):
            return

        return

    def sell_items(self):
        if(self.stopping):
            return

        self.inventory.sell_stuff()
        
    def item_was_sold(self):
        self.character.MUD_RETURN_ITEM_SOLD = False
        self.character.SELL_CHECK_FLAG = 1
        now = time.time()

        while(self.character.SELL_CHECK_FLAG == 1 and time.time() - now < 3.0):
            time.sleep(0.05)

        magentaprint("Bot: Time for sell check was %.1f." % round(time.time()-now, 1))
        return self.character.MUD_RETURN_ITEM_SOLD    


    def drop_items(self):
        
        if(self.stopping):
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

        if self.stopping:
            return

        self.smartCombat.target = monster
        self.smartCombat.run()
        
        # while(self.commandHandler.KillThread != None and self.commandHandler.KillThread
        #       and self.commandHandler.KillThread.stopping == False):
            
        #     if(self.character.BLACK_MAGIC):
        #         if(self.character.MANA >= black_magic_spell_cost):
        #             if(self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
        #                 self.commandHandler.user_cc(self.character.FAVOURITE_SPELL + " " + monster)
        #         else:
        #             self.commandHandler.stop_CastThread()
                    
        #     # TODO: restoratives (use when vig not keeping up or low mana)
        #     if (self.character.HEALTH <= (self.character.HEALTH_TO_HEAL)):
        #         if (self.character._class.id == "Mon"):
        #             magentaprint("Last Meditate Check: " + str(time.time() - self.character.LAST_MEDITATE))
        #             if((time.time() - self.character.LAST_MEDITATE) > 150):
        #                 self.commandHandler.process('meditate')
        #                 self.character.LAST_MEDITATE = time.time()
        #         if(self.character.MANA >= vigor_cost and self.character.KNOWS_VIGOR and
        #             self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
        #             self.commandHandler.user_cc("vig")
        #             self.commandHandler.stop_CastThread()
        #         #else:
        #             #self.use_restorative_items()


        #     # FLEE Checks
        #     if(self.character.HEALTH <= self.character.HEALTH_TO_FLEE):
        #         # We're done for!  Trust CommandHandler to get us out.  
        #         # It will turn around and stop botThread.
        #         self.stop()  
        #         self.commandHandler.user_flee() 

        #     time.sleep(0.05)

        # # OK the mob died or ran or I ran
        # self.commandHandler.stop_CastThread()    
        
        if monster in self.character.MOBS_ATTACKING:
            #magentaprint("Bot:engage_monster: Removing " + monster + " from MOBS_ATTACKING.")
            magentaprint("I believe the following is dead or gone: " + monster, False)
            self.character.MOBS_ATTACKING.remove(monster)
            
        return


    def get_items(self):
        if(self.stopping):
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