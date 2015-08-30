
import threading
from threading import Thread
import atexit 
import time
import re
from math import floor, ceil

from misc_functions import *
from BotReactions import GenericBotReaction
from CommandHandler import CommandHandler
from Inventory import Inventory
from Exceptions import *
from Database import *
from MudMap import MudMap
import Spells

class BotThread(threading.Thread):

    def __init__(self, character, commandHandler, mudReaderHandler, mud_map):
        Thread.__init__(self)
        self.stopping = False        
        
        self.character = character
        self.commandHandler = commandHandler
        self.mudReaderHandler = mudReaderHandler
        self.inventory = character.inventory
        self.smartCombat = commandHandler.smartCombat
        self.kill = commandHandler.smartCombat.kill
        self.cast = commandHandler.smartCombat.cast
        self.direction_list = []

        self.character.ACTIVELY_BOTTING = True

        self.no_exit_count = 0

        self.mud_map = mud_map
        create_tables()
        db.close()

        atexit.register(self.stop)

    def stop(self):
        magentaprint("Stopping bot = " + str(self.stopping))
        self.stopping = True
        self.character.ACTIVELY_BOTTING = False

    def is_stopping(self):
        return self.stopping

    def keep_going(self):
        self.stopping = False

    def sleep(self, duration):
        time.sleep(duration)

    def run(self):                    
        self.stopping = False 
        self.do_run_startup()

        # Here is where the fun begins.
        while not self.stopping:
            if self.stopping:
                break

            self.do_pre_go_actions()
            
            if len(self.direction_list) is 0:
                self.direction_list = self.decide_where_to_go()
                
            while len(self.direction_list) is not 0 and not self.stopping:
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
                        self.no_exit_count += 1
                        self.do_on_go_no_exit()
                        continue

                #now we add a hook for any actions in this new area    
                self.do_post_go_actions()
            self.do_after_directions_travelled()

        magentaprint("BotThread: finished now.")

    def go(self, exit_str):
        
        if self.stopping:
            return True
        
        wait_for_move_ready(self.character)
        self.kill.wait_until_ready()
        self.cast.wait_until_ready()
        magentaprint("Going " + exit_str + (". %.1f" % (time.time() - self.character.START_TIME)), False)

        self.character.GO_BLOCKING_MOB = ""
        self.character.GO_PLEASE_WAIT = False
        self.character.GO_NO_EXIT = False
        self.character.GO_TIMEOUT = False
        self.character.SUCCESSFUL_GO = False

        hook_found = self.do_go_hooks(exit_str)  # fans out 'areaidN' into real directions.
            # ... we need to wait for Cartography before this happens

        if not hook_found:
            if re.match("(.*?door)", exit_str):
                self.commandHandler.process("open " + exit_str)
                # self.commandHandler.process('door')
            # self.commandHandler.process("go " + exit_str)
            # self.commandHandler.go.execute(exit_str)
            self.commandHandler.go.persistent_execute(exit_str)
            # self.commandHandler.go.wait_for_flag()
            return self.commandHandler.go.result is 'success'
            return self.check_for_successful_go()
            # if re.match("(.*?door)", exit_str):
            #     self.commandHandler.process("open " + exit_str)
            # return self.go.persistent_execute(exit_str)
        else:
            return hook_found

    def check_for_successful_go(self):
        return self.mudReaderHandler.check_for_successful_go()

    ''' STATIC METHODS '''
    @staticmethod
    def has_ideal_stat(cur_value, ideal_value):
        return cur_value >= ideal_value 

    @staticmethod
    def can_use_timed_ability(last_use, timeout):
        # cooldown = time.time() - last_use

        # if timeout < cooldown:
        #     return True

        # return False
        return timeout < time.time() - last_use

    @staticmethod
    def can_cast_spell(current_mana, spell_cost, knows_spell):
        return knows_spell and current_mana >= spell_cost
    
    @staticmethod
    def should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items):
        should_heal = not BotThread.has_ideal_stat(current_health, ideal_health)

        if should_heal:
            can_cast_spell = BotThread.can_cast_spell(current_mana, heal_cost, knows_spell)

            if can_cast_spell or has_healing_items:
                should_heal = True
            else:
                should_heal = False

        return should_heal

    def has_ideal_mana(self):
        return BotThread.has_ideal_stat(self.character.MANA, self.character.MANA_TO_WAIT)

    def has_ideal_health(self):
        return BotThread.has_ideal_stat(self.character.HEALTH, self.character.HEALTH_TO_HEAL)

    def do_go_hooks(self, exit_str):
        #if you want to define custom hooks like sell_items / drop_items etc... you can do so here

        #add the path to a given areaid to out current direction_list
        if re.match("areaid[\d]*", exit_str):
            #magentaprint("go hook found with: " + str(self.direction_list), False)
            area_id = int(exit_str.replace("areaid", ""))
            self.direction_list.pop(0)
            
            try:
                path = self.mud_map.get_path(self.character.AREA_ID, area_id)
                
                if len(path) == 0:
                    self.direction_list = ["buffer"] + self.direction_list
                else:
                    self.direction_list = ["buffer"] + path + self.direction_list

            except Exception:
                magentaprint("BotThread.do_go_hooks() problem with go hook " + exit_str + ", unsuccessful go.")
                if len(self.direction_list) > 0:
                    self.direction_list.pop(0) #remove the areaid[/d]*
                return False
            #magentaprint("path added to list: " + str(self.direction_list), False)
            return True
        return False

    ''' Defined Hooks in Run() '''
    def do_run_startup(self):
        #self.set_up_automatic_ring_wearing()
        #setup heal reactions
        return

    def do_pre_go_actions(self):
        # We need a hook for chapel actions...
        # This is not before every go, just before (after) every direction list
        # (I think this in_chapel check will be unnecessary when another fix happens...
            # there's currently a bug where the direction list gets remade too often)
        if self.in_chapel():
            self.rest_and_check_aura()
            self.check_weapons()
            self.check_armour()

    def in_chapel(self):
        magentaprint("BotThread.in_chapel(): MUD_AREA is " + str(self.character.MUD_AREA))
        return self.character.AREA_ID == 2
        # return self.character.MUD_AREA.is_restorative

    def decide_where_to_go(self): #each logic thread will have to implement this function
        #self.direction_list = []
        raise NotImplementedError()

    def do_on_succesful_go(self):
        self.direction_list.pop(0)
        self.character.MOBS_JOINED_IN = [] 
        self.character.MOBS_ATTACKING = []
        self.no_exit_count = 0

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
        magentaprint("Bot: Check go timed out.  Could be lag.  Will try agian in 6 sec.")
        # This can happen when the system clock makes time.time() inconsistent.
        # Unless I can fix this I have to ignore this case and hope it worked.
        self.direction_list.pop(0)
        self.character.MOBS_JOINED_IN = [] 
        self.character.MOBS_ATTACKING = []
        self.sleep(6)

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
        # This method is only efficient in a healing area
        magentaprint("BotThread.rest_and_check_aura()")
        mana_to_wait = self.character.MAX_MANA - 2*(self.character._class.mana_tick + 2) 
            # MANA_TO_WAIT differentiates between hitting 'rest' and just hitting 
            # 'enter' a bunch (waiting vs resting)

        aura_updated = self.update_aura()  # Most reasonable reason to fail is if we have no mana

        self.chapel_heal_up()  
            # TODO: Keep track of when ticks are coming and how big they'll be, and avoid vigging 
            # away all the mana for characters with low piety, whose vigors will not do much, 
            # and may just be one tick away from good health. 

        if self.character.MANA < mana_to_wait:
            self.rest_until_ready()
        elif self.character.MANA < self.mana_to_go:
            self.wait_for_mana()
                   
        if not aura_updated:
            aura_updated = self.update_aura()

        if aura_updated:
            self.aura_updated_hook()
    
        if self.character.level > 3 and self.character.MAX_MANA > 10:
            self.heal_up()
            self.wait_for_mana()  
        else:
            # magentaprint("Resting for health", False)
            # Probably not the greatest logic but low level characters will need 
            # to gain health other than healing up.
            self.rest_for_health()

        # self.buff_up()


    @property
    def mana_to_go(self):
        if self.smartCombat.black_magic: 
            if self.character.maxMP % 3 == 0 and self.character.maxMP < 13:
                return self.character.maxMP
            elif self.character.maxMP < 25:
                return self.character.maxMP - 1
            else:
                return self.character.maxMP - 2
        else:
            if self.character.maxMP % 2 == 0 and self.character.maxMP < 13:
                return self.character.maxMP
                # We wait for an even number because only cast vigor (2 mana)
            elif self.character.maxMP < 25:
                return self.character.maxMP - 1     
            else:
                return self.character.maxMP - 2

    @property
    def health_to_go(self):
        if self.character.level < 4:
            return self.character.maxHP
        elif self.character.level < 6:
            return self.character.maxHP - 1
        elif self.character.level < 8:
            return self.character.maxHP - 2
        else:
            return self.character.maxHP - 3

    def chapel_heal_up(self):
        # This function casts vigor until the hp/mp are balanced so that 
        # we tick our way up to max hp/mp.  (It won't stupidly drain all mana on vigging)

        # If we can get hp/mp in sync to the same # of ticks, then do that.
        # If too much hp, go fight to bring hp down.  If too much mp, vig to balance.
        # After vigging and resting a full mana pool, hp may still not be very high, 
        # and in that case, keep resting since benefits should be active.

        magentaprint("In chapel_heal_up.")
        heal_cost = 2

        if self.stopping:
            return

        if self.character.HEALTH >= self.health_to_go:
            return

        self.do_heal_skills()

        if self.character.HEALTH >= self.health_to_go:
            return

        if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
            self.cast.cast('v')
            self.cast.wait_for_flag()

            if self.character.HEALTH >= self.health_to_go:
                return

            self.cast.start_thread('v')
        
        self.character.HAS_RESTORE_ITEMS = False

        if not self.character.KNOWS_VIGOR:
            return

        vig = 2
        chapel = 2
        maxHP = self.character.maxHP
        maxMP = self.character.maxMP
        mana_tick = self.character._class.mana_tick
        magentaprint("Health ticks needed: " + str(self.health_ticks_needed()) + ", Mana ticks needed: " + str(self.mana_ticks_needed()))

        # while   (self.health_ticks_needed() > self.mana_ticks_needed() or 
        #         self.character.MANA - (maxMP % mana_tick+chapel) % (mana_tick+chapel) >= 2) and (
        while   (self.health_ticks_needed() > self.mana_ticks_needed() and 
                self.character.MANA >= vig and 
                not self.ready_for_combat() and 
                not self.stopping):
                # self.character.mana_tick+2 % self.character.maxMP - self.character.MANA > 2:
                # self.character.maxMP - self.character.MANA % self.character.mana_tick+chapel - vig >= 0: #self.character.mana_tick + vig - chapel:
                # Laurier does math!  (Mathing out whether we should vig or in the chapel)
            self.do_heal_skills()

            # if self.engage_any_attacking_mobs():
            #     if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
            #         self.cast.start_thread('v')
            self.cast.wait_until_ready()
            self.engage_any_attacking_mobs()
            self.cast.cast('v')

        self.cast.stop()  # Unnecessary

        # while BotThread.should_heal_up(self.character.HEALTH, self.character.HEALTH_TO_HEAL,
        #         self.character.MANA, heal_cost, self.character.KNOWS_VIGOR, self.character.HAS_RESTORE_ITEMS) and not self.stopping:

        #     self.do_heal_skills()

        #     if self.engage_any_attacking_mobs():
        #         if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
        #             self.cast.start_thread('v')
            
        #     #self.use_restorative_items() #spam them!!!

        #     self.sleep(0.05)

        # self.cast.stop()

    def health_ticks_needed(self):
        return (self.character.maxHP - self.character.HEALTH) / (self.character.hp_tick + 3)

    def mana_ticks_needed(self):
        return (self.character.maxMP - self.character.MANA) / (self.character._class.mana_tick + 2)

    def do_rest_hooks(self):
      return

    def aura_updated_hook(self):
      return

    def rest_until_ready(self):
        magentaprint("BotThread.rest_until_ready()")

        # Rest until one of hp or mp is maxed.  This way we aren't waiting for both.
        # Hopefully things are somewhat balanced.  If things are unbalanced, benefits 
        # of resting can be used to balance, and if it's a shorter rest, then just go 
        # when one of them is maxed (use ready_for_combat as a mimimum, if after resting
        # we aren't ready for combat, erhm, well that's kind of ridiculous.)

        # TODO: keep resting if benefitting from resting until maxed.

        if self.neither_is_maxed or self.one_is_too_low and not self.stopping:
            self.commandHandler.process("rest")            

        while self.neither_is_maxed or self.one_is_too_low and not self.stopping:
            if self.engage_any_attacking_mobs():
                self.commandHandler.process("rest")
            self.sleep(0.1)

    @property 
    def neither_is_maxed(self):
        return self.character.HEALTH < self.character.maxHP and self.character.MANA < self.character.maxMP

    @property
    def one_is_too_low(self):
        return self.character.HEALTH < self.health_to_go or self.character.MANA < self.mana_to_go

    def wait_for_mana(self):
        magentaprint("BotThread.wait_for_mana()")
        while self.character.MANA < self.mana_to_go and not self.stopping:
            self.sleep(3.5)
            self.engage_any_attacking_mobs()
            self.commandHandler.process('')
            self.sleep(1.2)  # Wait for prompt to respond before checking MANA again.
        
    def rest_for_health(self):
        magentaprint("BotThread.rest_for_health()")
        if self.has_ideal_health():
            return

        self.do_heal_skills()
        
        self.commandHandler.process("rest")            

        # magentaprint(self.has_ideal_health(), False)

        while(not self.has_ideal_health() and not self.stopping):            

            if(self.engage_any_attacking_mobs()):
                self.commandHandler.process("rest")
            elif (self.do_heal_skills()):
                self.commandHandler.process("rest")

            self.sleep(1.2)

        # magentaprint("Stopping rest for health",False)

        return

    def update_aura(self):
        if self.stopping or self.character.ACTIVELY_MAPPING or not Spells.showaura in self.character.spells:
            return False

        self.cast.update_aura(self.character)

        if self.cast.result is not 'success': # Probably no mana since spell fail gets spammed
            return False
        else:
            return True

        # if self.character.level < 3 or not \
        #         BotThread.can_use_timed_ability(self.character.AURA_LAST_UPDATE, 480):
        # if not Spells.showaura in self.character.spells:
            # magentaprint("Last aura update %d seconds ago." % round(time.time() - self.character.AURA_LAST_UPDATE))
            # return True   

        # self.cast.wait_until_ready()
        # aura_matched = False

        # while not aura_matched and self.character.MANA > 0 and not self.stopping:
        #     self.cast.cast('show')
        #     # aura_matched = self.mudReaderHandler.wait_for_aura_match() 
        #     self.cast.wait_for_flag()

            
        # if aura_matched:
        #     self.character.AURA_LAST_UPDATE = time.time()
        #     return True

        # return False  # Ran out of mana

    def heal_up(self):
        magentaprint("In heal_up.")
        heal_cost = 2

        if self.stopping:
            return

        if self.has_ideal_health():
            return

        self.do_heal_skills()

        if self.has_ideal_health():
            return

        if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
            self.cast.execute('v')
            self.cast.wait_for_flag()

            if self.has_ideal_health():
                return

            self.cast.start_thread('v')
        
        self.character.HAS_RESTORE_ITEMS = False

        while BotThread.should_heal_up(self.character.HEALTH, self.character.HEALTH_TO_HEAL,
                self.character.MANA, heal_cost, self.character.KNOWS_VIGOR, self.character.HAS_RESTORE_ITEMS) and not self.stopping:

            self.do_heal_skills()

            if self.engage_any_attacking_mobs():
                if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
                    self.cast.start_thread('v')
            
            #self.use_restorative_items() #spam them!!!

            self.sleep(0.05)

        self.cast.stop()

    def is_character_class(self, class_str):
        return self.character._class.id == class_str

    def buff_up(self):
        self.do_buff_skills()
        if BotThread.can_use_timed_ability(self.character.LAST_BUFF, 180):
            self.use_buff_items()
            self.character.LAST_BUFF = time.time()

    def use_buff_items(self):
        if self.inventory.has("milky potion"):
            self.commandHandler.process('drink milky')
        elif self.inventory.has("steel bottle"):
            self.commandHandler.process('drink steel')
        else:
            self.character.HAS_BUFF_ITEMS = False

    def use_restorative_items(self):
        if self.inventory.has("small restorative"):
            self.commandHandler.process('drink restorative')
            # large restorative
        elif self.inventory.has("scarlet potion"):
            self.commandHandler.process('drink scarlet')
        elif self.inventory.has("tree root"):
            self.commandHandler.process('eat root')
            # white potion
        else:
            self.character.HAS_RESTORE_ITEMS = False

    def check_weapons(self):
        if self.stopping:
            return

    def check_armour(self):
        if self.stopping:
            return

    def sell_items(self):
        if self.stopping:
            return
        
        self.inventory.sell_stuff()
        
    def item_was_sold(self):
        self.character.MUD_RETURN_ITEM_SOLD = False
        self.character.SELL_CHECK_FLAG = 1
        now = time.time()

        while self.character.SELL_CHECK_FLAG == 1 and time.time() - now < 3.0:
            self.sleep(0.05)

        magentaprint("Bot: Time for sell check was %.1f." % round(time.time()-now, 1))
        return self.character.MUD_RETURN_ITEM_SOLD    


    def drop_items(self):
        if self.stopping:
            return
        self.inventory.drop_stuff()

    def decide_which_mob_to_kill(self, monster_list):
        monster_list = monster_list[:]                 

        #avoid fighting around mobs that join in
        for mob in monster_list:
            if re.search("town guard", mob) or \
               re.search("town crier", mob) or \
               re.search("clown", mob) or \
               re.search("bouncer", mob):
                return ""

        if self.character.chase_mob is not "":
            mob = self.character.chase_mob
            self.character.chase_mob = ""
            self.character.chase_dir = ""

            return mob
        
        #find a new monster to kill
        for mob in monster_list:
            if mob in self.character.MONSTER_KILL_LIST:
                return mob
            
        return ""

    def do_buff_skills(self):
        if self.character._class is not None:
            for skill in self.character._class.buff_skills:
                if skill.up():
                    skill.execute()
                    skill.wait_for_flag()
                    return skill.result is 'success'

    def do_combat_skills(self, target):
        if self.character._class is not None:
            for skill in self.character._class.combat_skills:
                if skill.up():
                    skill.execute(target)
                    skill.wait_for_flag()
                    return skill.result is 'success'
        return False

    def do_heal_skills(self):
        if self.character._class is not None:
            for skill in self.character._class.heal_skills:
                if skill.up():
                    skill.execute()
                    skill.wait_for_flag()
                    return skill.result is 'success'
        return False

    def engage_monster(self, monster):
        if self.stopping:
            return

        self.smartCombat.target = monster
        self.smartCombat.spell = self.smartCombat.favourite_spell
        self.smartCombat.run()
        # self.smartCombat.run()

        # vigor_cost = 2
        # black_magic_spell_cost = self.character.SPELL_COST
        
        # self.buff_up()
        # self.do_combat_skills(monster)

        # magentaprint("Engage: " + monster)
        # ifled = False

        # self.commandHandler.user_kk(monster)
        # self.sleep(0.5)  # Keeps attacking and magic out of sync

        # while(self.commandHandler.KillThread != None and self.commandHandler.KillThread
        #       and self.commandHandler.KillThread.stopping == False):

        #     if(BotThread.can_cast_spell(self.character.MANA, black_magic_spell_cost, self.character.BLACK_MAGIC)):
        #         if(self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
        #             magentaprint("Starting black magic cast thread: " + monster)
        #             self.commandHandler.user_cc(self.character.FAVOURITE_SPELL + " " + monster)
        #         else:
        #             self.commandHandler.stop_CastThread()
            
        #     # TODO: restoratives (use when vig not keeping up or low mana)
        #     if (not self.has_ideal_health()):

        #         self.do_heal_skills()
                
        #         if (BotThread.can_cast_spell(self.character.MANA, vigor_cost, self.character.KNOWS_VIGOR)):
        #             if( self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
        #                 magentaprint("Starting vigor cast thread")
        #                 self.commandHandler.user_cc("vig")
        #         else:
        #             self.commandHandler.stop_CastThread()
        #         #else:
        #             #self.use_restorative_items()


        #     ifled = False
        #     # FLEE Checks
        #     if(self.character.HEALTH <= self.character.HEALTH_TO_FLEE):
        #         # We're done for!  Trust CommandHandler to get us out.  
        #         # It will turn around and stop botThread.
        #         self.do_flee_hook()
        #         ifled = True

        #         # OK the mob died or ran
        #         self.commandHandler.stop_CastThread() 

        #     self.sleep(0.05)   

        if self.character.chase_mob is not "":
            #engage mobs which are already fighting us
            magentaprint("BotThread chasing mob, pushing onto direction list!")
            if self.character.AREA_ID is not None:
                go_hook = "areaid" + str(self.character.AREA_ID)
                self.direction_list.insert(0, go_hook) #should be this area
            else:
                go_hook = "areaid45"
                self.direction_list.insert(0, go_hook) #should be this area

            self.go(self.character.chase_dir)
            self.character.chase_dir = ""
            self.character.chase_mob = ""

        # #magentaprint("end of enage dir list: " + str(self.direction_list), False)

        if monster in self.character.MOBS_ATTACKING:
            self.character.MOBS_ATTACKING.remove(monster)

    def do_flee_hook(self):
        self.stop()  
        self.commandHandler.user_flee() 

    def get_items(self):
        if self.character.chase_mob == "" and not self.stopping: 
            self.commandHandler.process("ga")  

    def engage_mobs_who_joined_in(self):
        while self.character.MOBS_JOINED_IN != []:
            self.engage_monster(self.character.MOBS_JOINED_IN[0])
            self.character.MOBS_JOINED_IN = self.character.MOBS_JOINED_IN[1:]
            self.get_items()
    
    def engage_any_attacking_mobs(self):
        engaged = False

        while self.character.MOBS_ATTACKING != []:
            engaged = True
            self.engage_monster(self.character.MOBS_ATTACKING[0])
            self.get_items()

        return engaged
    
    def ready_for_combat(self):
        return self.character.HEALTH >= self.character.HEALTH_TO_HEAL and self.character.MANA >= self.character.MANA_TO_ENGAGE
        # return (self.has_ideal_health() and
        #         self.has_ideal_mana())


