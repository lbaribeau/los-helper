
import re

from bots.BotThread import BotThread
from misc_functions import magentaprint
from reactions.BotReactions import GenericBotReaction
from Exceptions import *
from command import Spells
from math import floor, ceil

class GrindThread(BotThread):
    def __init__(self, character, commandHandler, mudReaderHandler, mud_map):
        super().__init__(character, commandHandler, mudReaderHandler, mud_map)
        self.loot_threshold = 1  # the amount of loot to collect before selling

    def do_run_startup(self):
        if not self.is_character_class("Mon"):
          self.set_up_automatic_ring_wearing()

        if self.direction_list is None:
          self.direction_list = [] #could append areaid45

    def do_rest_hooks(self):
        pass

    def aura_updated_hook(self):
        pass

    def do_pre_go_actions(self):
        if self.in_chapel():
            self.rest_and_check_aura()
            self.check_weapons()
            self.check_armour()

    def do_go_hooks(self, exit_str):
      #if you want to define custom hooks like sell_items / drop_items etc... you can do so here

      if (exit_str == "nw" or exit_str == "ne" or
           exit_str == "sw" or exit_str == "se" or
           exit_str == 'n' or exit_str == 'e' or
           exit_str == 's' or exit_str == 'w'):
            # self.commandHandler.process(exit_str)
            # return self.check_for_successful_go() 
            # return self.check_for_successful_go() 
            # return self.go(exit_str)   # Erhm self.go calls us, not the other way around
            self.commandHandler.go.persistent_execute(exit_str)
            return self.commandHandler.go.success
      elif exit_str == "prepare":
          self.commandHandler.process(exit_str)
          return True
      elif exit_str == "sell_items":
          self.sell_items()
          return True
      elif exit_str == "drop_items":
          self.drop_items()
          return True

      return super().do_go_hooks(exit_str)

    def do_on_succesful_go(self):
        if len(self.direction_list) != 0:
          self.direction_list.pop(0)
  
        self.character.MOBS_JOINED_IN = [] 
        self.character.MOBS_ATTACKING = []

    def do_on_blocking_mob(self):
        self.engage_monster(self.character.GO_BLOCKING_MOB)
        self.get_items()
        self.character.GO_BLOCKING_MOB = ""
        self.engage_mobs_who_joined_in()
        self.engage_any_attacking_mobs()
        self.check_weapons()
        
        if not self.character.BLACK_MAGIC:
            self.heal_up()

    def do_post_go_actions(self):
        #here we would implement combat or whatever other other actions we want to do before we decide where to go again
        # Maybe this is more for do_on_successful_go()(?)
        if self.ready_for_combat():
            new_target = self.decide_which_mob_to_kill(self.character.MONSTER_LIST)
        else:
            new_target = ""
            magentaprint("TrackGrindThread.do_post_go_actions() calling do_rest_hooks()")
            # Commented - I don't understand what do_rest_hooks is supposed to do at all...
            # self.do_rest_hooks()

        while new_target != "" and not self.is_stopping():
            # MudReader maintains MONSTER_LIST pretty well by
            # adding and removing.  
            # It will not remove from MOBS_JOINED_IN nor 
            # MOBS_ATTACKING because the three lists can contain 
            # common mobs.  So before engaging a mob in one of the 
            # latter two lists the bot should check that it is 
            # still in the MONSTER_LIST.  Also be mindful of timing:
            # MOBS_ATTACKING might not be populated as soon as the 
            # bot enters the room - that's why they are engaged last
            # (as a cleanup).

            # Now we can reference MONSTER_LIST again.  Note that
            # MudReader has already removed all of the mobs that we
            # killed.  (That's in fact how we knew combat was over)
            # The higher priority mobs were in the other lists 
            # and will also have been removed from MONSTER_LIST
            
            magentaprint("Targeting: " + new_target)

            self.engage_monster(new_target)
            self.get_items()
            self.engage_mobs_who_joined_in()
            self.engage_any_attacking_mobs()
            self.check_weapons()
            
            if (not self.character.BLACK_MAGIC):
                self.heal_up()
            
            if(self.ready_for_combat()):
                magentaprint("Picking a new target since " + new_target + " was defeated")
                new_target = self.decide_which_mob_to_kill(self.character.MONSTER_LIST)
            else:
                new_target = ""
        return

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
        
        self.character.HAS_RESTORE_ITEMS = False

        if not self.character.KNOWS_VIGOR:
            return

        self.cast.wait_until_ready()
        vig = 2
        chapel = 2
        maxHP = self.character.maxHP
        maxMP = self.character.maxMP
        mana_tick = self.character._class.mana_tick
        # while   (self.health_ticks_needed() > self.mana_ticks_needed() or 
        #         self.character.MANA - (maxMP % mana_tick+chapel) % (mana_tick+chapel) >= 2) and (
        while   (self.health_ticks_needed() > self.mana_ticks_needed() and 
                self.character.MANA >= vig and 
                not self.ready_for_combat() and 
                not self.stopping):
                # self.character.mana_tick+2 % self.character.maxMP - self.character.MANA > 2:
                # self.character.maxMP - self.character.MANA % self.character.mana_tick+chapel - vig >= 0: #self.character.mana_tick + vig - chapel:
                # Laurier does math!  (Mathing out whether we should vig or in the chapel)
            magentaprint("Health ticks needed: " + str(self.health_ticks_needed()) + ", Mana ticks needed: " + str(self.mana_ticks_needed()))
            self.do_heal_skills()

            # if self.engage_any_attacking_mobs():
            #     if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
            #         self.cast.start_thread('v')
            self.engage_any_attacking_mobs()
            self.cast.cast('v')
            self.cast.wait_for_flag()
            self.cast.wait_until_ready()

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

        if not self.cast.success:  # Probably no mana since spell fail gets spammed
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
        # TODO: class Sell(Command)  - Get rid of these all caps flag variables and copypasta polling code
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
                    return skill.success

    def do_combat_skills(self, target):
        if self.character._class is not None:
            for skill in self.character._class.combat_skills:
                if skill.up():
                    skill.execute(target)
                    skill.wait_for_flag()
                    return skill.success
        return False

    def do_heal_skills(self):
        if self.character._class is not None:
            for skill in self.character._class.heal_skills:
                if skill.up():
                    skill.execute()
                    skill.wait_for_flag()
                    return skill.success
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
        # while self.character.MOBS_JOINED_IN != []:
        #     self.engage_monster(self.character.MOBS_JOINED_IN[0])
        #     self.character.MOBS_JOINED_IN = self.character.MOBS_JOINED_IN[1:]
        #     self.get_items()
        while self.character.mobs.attacking:
            self.engage_monster(self.character.mobs.attacking[0])
            # self.character.mobs.attacking = self.character.mobs.attacking[1:]
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


