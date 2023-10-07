
import re
import pdb
import time
from math import floor, ceil

from bots.BotThread import BotThread
from db.Mob import Mob
from misc_functions import magentaprint, get_timeint
from reactions.BotReactions import GenericBotReaction
from reactions.ring_reaction import RingWearingReaction
from Exceptions import *
from comm import Spells
from db.MudItem import MudItem
from db.AreaStoreItem import AreaStoreItem
from Aura import Aura

class GrindThread(BotThread):
    aura = None
    aura_timer = 300
    aura_refresh = 300
    healing_area = "areaid2"

    def __init__(self, character, command_handler, mudReaderHandler, mud_map):
        super().__init__(character, command_handler, mudReaderHandler, mud_map)
        self.loot_threshold = 1  # the amount of loot to collect before selling
        self.run_kills = 0
        self.last_aura_refresh_kills = 0

        if self.character._class.is_evil():
            self.healing_area = "areaid2"

    def do_run_startup(self):
        pass
        # if not self.is_character_class("Mon"):
        #   self.set_up_automatic_ring_wearing()
        # if self.direction_list is None:
        #   self.direction_list = [] #could append areaid45

    def do_rest_hooks(self):
        pass

    def aura_updated_hook(self):
        pass

    def do_pre_go_actions(self):
        # TrackGrind overrides this...
        if self.in_chapel():
            self.rest_and_check_aura()
            # self.check_weapons()  #TODO: shopping doesn't work everywhere
            # self.check_armour()

    def do_go_hooks(self, exit_str):
        # Commenting: return False here to get BotThread (parent) to execute the 'go'
        # if (exit_str == "nw" or exit_str == "ne" or
        #    exit_str == "sw" or exit_str == "se" or
        #    exit_str == 'n' or exit_str == 'e' or
        #    exit_str == 's' or exit_str == 'w'):
        #     # self.command_handler.process(exit_str)
        #     # return self.check_for_successful_go()
        #     # return self.check_for_successful_go()
        #     # return self.go(exit_str)   # Erhm self.go calls us, not the other way around
        #     self.command_handler.go.persistent_execute(exit_str)
        #     return self.command_handler.go.success
        if exit_str == "sprepare":
            self.command_handler.process(exit_str)
            return True
        elif exit_str == "sell_items":
            # if we're in the pawn shop then sell stuff
            self.sell_items()
            return True
        elif exit_str == "drop_items":
            self.drop_items()
            return True
        elif re.match("dobuy.+?", exit_str):
            return self.buy_and_wield(exit_str)
        else:
            return super().do_go_hooks(exit_str)

    def buy_and_wield(self, exit_str):
        magentaprint("go hook found with: " + str(self.direction_list), False)
        item = exit_str.replace("dobuy", "")

        if self.buy(item):
            return self.wield(item)
        else:
            return False

    def buy(self, item):
        self.command_handler.buy.execute(item.partition(' ')[0])  # TODO: ensure that the correct item is bought
        self.command_handler.buy.wait_for_flag()
        # I'm hacking here.  I intend start a new Grind thread to do this properly.
        if self.command_handler.buy.cant_carry:
            # Maybe we're carrying a broken one
            # magentaprint("GrindThread.dobuy() reference: " + str(self.inventory.get_reference(item)))
            self.command_handler.drop.execute(self.inventory.get_reference(item))
            self.command_handler.drop.wait_for_flag()
            if not self.command_handler.drop.success:
                magentaprint("buy_and_wield() failed!")
                self.command_handler.process('rest')
                self.command_handler.quit()
                return False
            else:
                self.command_handler.buy.execute(item.partition(' ')[0])
                self.command_handler.buy.wait_for_flag()

        if self.command_handler.buy.success:
            magentaprint("GrindThread.buy_and_wield adding %s." % str(item))
            self.inventory.add(item)
            return True
        else:
            self.command_handler.process('rest')
            self.command_handler.quit()
            # crash  # failed to buy weapon
            return False

    def wield(self, item):
        return self.smartCombat.try_weapon(item)

    def do_on_blocking_mob(self):
        self.engage_monster(self.character.GO_BLOCKING_MOB)
        self.character.GO_BLOCKING_MOB = ""
        self.engage_mobs_who_joined_in()
        self.engage_any_attacking_mobs()
        self.check_weapons()  # TODO: shopping doesn't work everywhere

        if not self.character.BLACK_MAGIC:
            self.heal_up()

    def do_on_successful_go(self):
        super().do_on_successful_go() 

    def do_regular_actions(self):
        if self.character.mobs.chase == "" and self.character.MONSTER_KILL_LIST_TEMP != []:
            self.character.MONSTER_KILL_LIST_TEMP = []
            self.character.MONSTER_KILL_LIST = self.character.MONSTER_KILL_LIST

        if self.character.mobs.chase != '':
            self.character.MONSTER_KILL_LIST_TEMP = self.character.MONSTER_KILL_LIST
            self.character.MONSTER_KILL_LIST = []
            # new_target = self.character.mobs.chase
            new_target = ""
            self.character.mobs.chase = ''  # It should be a chase list
            self.character.mobs.chase_exit = ''
        elif self.ready_for_combat():
            new_target = self.decide_which_mob_to_kill(self.character.mobs.list)
        else:
            new_target = ""
            # magentaprint("TrackGrindThread.do_post_go_actions() calling do_rest_hooks()") # Out of date print...
            magentaprint("GrindThread.regular_actions() not ready for combat")
            return
            # Commented - I don't understand what do_rest_hooks is supposed to do at all...
            # self.do_rest_hooks()

        while new_target != "" and not self.stopping:
            # MudReader maintains MONSTER_LIST pretty well by adding and removing.
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

            # if using a thief or assassin then hide, check if hidden
            # then have smart combat backstab

            self.pre_combat_actions(new_target)
            mob_target = Mob.get_mob_by_name(new_target)
            
            max_attempts = 1
            if not self.is_mob_weak(mob_target):
                max_attempts = 2

            if mob_target is not None and not mob_target.is_hostile and (self.is_character_class('Thi') or self.is_character_class('Ass')):
                magentaprint("persistent backstab prep started", False)
                hidden = self.persistently_take_action(self.backstab_prep, timeout=2)
                magentaprint("persistent backstab prep done", False)

                if hidden:
                    magentaprint("we're hidden so sleeping for a bit", False)
                    time.sleep(2.5)
                else:
                    magentaprint("failed to hide", False)

            self.engage_monster(new_target)
            self.engage_mobs_who_joined_in()
            self.engage_any_attacking_mobs()
            self.check_weapons()  # TODO: shopping doesn't work everywhere

            if not self.character.BLACK_MAGIC:
                self.heal_up()

            if self.ready_for_combat():
                magentaprint("GrindThread picking a new target since " + new_target + " was defeated")
                new_target = self.decide_which_mob_to_kill(self.character.mobs.list)
            else:
                new_target = ""

    def backstab_prep(self):
        success = False
        for skill in self.character._class.pre_combat_skills:
            if skill.up() and skill.command == 'hid':
                skill.execute()
                skill.wait_for_flag()
                success = skill.success

        self.character.HIDDEN = success
        return success

    def is_mob_weak(self, mob_target, level_diff=3):
        if mob_target is None or mob_target.level is None or mob_target.level == "":
            return False
        
        mob_level = mob_target.level
        if mob_target.difficulty_rating is not None and mob_target.difficulty_rating != "":
            mob_level += mob_target.difficulty_rating

        return mob_level < (self.character.level - level_diff)

    def persistently_take_action(self, action_func, timeout=20):
        success = False
        start_time = get_timeint()
        seconds_since_start = (get_timeint() - start_time).total_seconds()

        while seconds_since_start < timeout and not success:
            for i in range(0,20):
                success = action_func()
                self.sleep(0.25)
                if success:
                    break
            self.engage_any_attacking_mobs()
            seconds_since_start = (get_timeint() - start_time).total_seconds()
        
        return success

    def persistently_try_to_buff(self):
        magentaprint("GrindThread.persistently_try_to_buff() started", False)
        self.persistently_take_action(self.use_buff_ability)
        magentaprint("GrindThread.persistently_try_to_buff() finished", False)
        # buff_attempt = 0
        # buff_success = False

        # while not buff_success and not self.character.is_buffed() and buff_attempt < 4:
        #     buff_success = self.use_buff_ability()
        #     if self.character.mobs.chase != '' or \
        #         self.character.mobs.attacking != []:
        #         break

        #     if not buff_success:
        #         self.sleep(6)

        #     buff_attempt += 1
        #     first = False

    def pre_combat_actions(self, target):
        mob_target = Mob.get_mob_by_name(target)
        if (not self.is_mob_weak(mob_target, 5) or \
        (self.inventory.count_large_restoratives() < 5 and not self.is_mob_weak(mob_target, 7))) and\
            self.character.buff_ability_up():
            self.persistently_try_to_buff()


    def set_up_automatic_ring_wearing(self):
        """ Makes some BotReactions so that when MudReaderHandler sees us
        pick up a ring, we'll wear it."""
        # r = GenericBotReaction("(?s)You get .+? an? .+? ring((,.+?\.)|(\.))", self.command_handler, "wear all")  # Regex problem
        # self.mudReaderHandler.register_reaction(r)
        ring_reaction = RingWearingReaction(self.character.inventory, self.command_handler)
        self.mudReaderHandler.register_reaction(ring_reaction)
        #Todo: fix for case where there's ring mail in the inventory or multiple rings are dropped

    def rest_and_check_aura(self):
        # This method is only efficient in a healing area
        magentaprint("BotThread.rest_and_check_aura()", False)
        mana_to_wait = 0
        is_slow_steady = self.character.MANA_TO_ENGAGE > 0
        if is_slow_steady:
            mana_to_wait = self.character.maxMP - 2*(self.character._class.mana_tick + 2)
            # MANA_TO_WAIT differentiates between hitting 'rest' and just hitting
            # 'enter' a bunch (waiting vs resting)

        aura_updated = self.update_aura()  # Most reasonable reason to fail is if we have no mana

        # if is_slow_steady:
        #     self.chapel_heal_up()
            # TODO: Keep track of when ticks are coming and how big they'll be, and avoid vigging
            # away all the mana for characters with low piety, whose vigors will not do much,
            # and may just be one tick away from good health.

        if self.character.MANA < mana_to_wait:
            self.rest_until_ready()
        elif (self.character.MANA < self.mana_to_go) and self.character.NEEDS_MAGIC:
            # trigger any heal bots in the room
            magentaprint("Resting for mana", False)
            self.command_handler.process("rest")
            self.wait_for_mana()

        if not aura_updated:
            aura_updated = self.update_aura()

        # if self.character.level > 3 and self.character.maxMP > 10:
        #     self.heal_up()
        #     self.wait_for_mana()
        # else:
            # magentaprint("Resting for health", False)
            # Probably not the greatest logic but low level characters will need
            # to gain health other than healing up.
        if (not self.character.BLACK_MAGIC) and is_slow_steady:
            self.heal_up()
        self.rest_for_health()

        self.buff_up()
        self.use_extra_bless_item()

    @property
    def mana_to_go(self):
        if self.character.NEEDS_MAGIC:
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
        return 0

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
        # If too much hp, go fight to bring hp down*.  If too much mp, vig to balance.
        # After vigging and resting a full mana pool, hp may still not be very high,
        # and in that case, keep resting since benefits should be active.
        # *requires strong enemy for black magic users
        if self.character.info.pty >= 12:
            magentaprint("In chapel_heal_up.")

            if self.stopping or self.character.HEALTH >= self.health_to_go:
                return

            # don't use heal abilities in the chapel
            # only monks and bards have them and it's a waste of the cooldown
            # if not self.is_character_class('Mon'):
            #     self.do_heal_skills()

            # if self.character.HEALTH >= self.health_to_go or not any(s.startswith(Spells.vigor) for s in self.character.spells):
            if True and (self.character.HEALTH >= self.health_to_go or Spells.vigor not in self.character.spells):
                return

            self.cast.wait_until_ready()
            vig = 2
            chapel = 2  # additional hp tick amount
            maxHP = self.character.maxHP
            maxMP = self.character.maxMP
            
            mana_tick = 2
            # if mana_tick exists on character then
            if hasattr(self.character, 'mana_tick'):
                mana_tick = self.character.mana_tick
            # while   (self.health_ticks_needed() > self.mana_ticks_needed() or
            #         self.character.MANA - (maxMP % mana_tick+chapel) % (mana_tick+chapel) >= 2) and (
            while   (self.health_ticks_needed() > self.mana_ticks_needed() and
                    self.character.MANA >= vig and self.character.MANA_TO_ENGAGE != 0 and
                    not self.ready_for_combat() and
                    not self.stopping):
                    # self.character.mana_tick+2 % self.character.maxMP - self.character.MANA > 2:
                    # self.character.maxMP - self.character.MANA % self.character.mana_tick+chapel - vig >= 0: #self.character.mana_tick + vig - chapel:
                    # Laurier does math!  (Mathing out whether we should vig or in the chapel)
                magentaprint("Health ticks needed: " + str(round(self.health_ticks_needed(), 1)) + ", Mana ticks needed: " + str(round(self.mana_ticks_needed(), 1)))

                # if not self.is_character_class('Mon') and self.do_heal_skills():
                #     continue
                #     # elif self.inventory.count_small_restoratives() > 7:
                # #     self.command_handler.use.wait_until_ready()
                # #     self.command_handler.use.small_healing_potion()
                # #     self.command_handler.use.wait_for_flag()
                # else:
                #     # if self.engage_any_attacking_mobs():
                #     #     if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
                #     #         self.cast.start_thread('v')
                self.cast.cast('v')
                self.cast.wait_for_flag()
                self.cast.wait_until_ready()

                self.engage_any_attacking_mobs()

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

        if (self.neither_is_maxed or self.one_is_too_low) and not self.stopping:
            magentaprint("rest until ready start", False)
            self.command_handler.process("rest")

        while (self.neither_is_maxed or self.one_is_too_low) and not self.stopping:
            if self.engage_any_attacking_mobs():
                magentaprint("resting until ready", False)
                self.command_handler.process("rest")
            self.sleep(0.1)

    @property
    def neither_is_maxed(self):
        return self.character.HEALTH < self.character.maxHP and self.character.MANA < self.character.maxMP

    @property
    def one_is_too_low(self):
        return self.character.HEALTH < self.health_to_go or self.character.MANA < self.mana_to_go or self.character.MANA < self.character.MANA_TO_ENGAGE

    def wait_for_mana(self):
        magentaprint("BotThread.wait_for_mana()")
        while self.character.MANA < self.mana_to_go and not self.stopping:
            for i in range(0,20):
                self.sleep(0.25)
                if self.stopping:
                    return
            self.engage_any_attacking_mobs()
            self.command_handler.process('')

    def rest_for_health(self):
        magentaprint("BotThread.rest_for_health()", False)

        if self.has_ideal_health():
            return

        if not self.character.info.pty < 12:
            self.do_heal_skills()
        magentaprint("rest for health start", False)
        self.command_handler.process("rest")
        # magentaprint(self.has_ideal_health(), False)

        while not self.has_ideal_health() and not self.stopping:
            magentaprint("GrindThread.rest_for_health() stopping is: " + str(self.stopping))
            if self.engage_any_attacking_mobs():
                magentaprint("resting for health", False)
                self.command_handler.process("rest")
            elif not self.character.info.pty < 10:
                if self.do_heal_skills():
                    magentaprint("resting for health after healing", False)
                    self.command_handler.process("rest")

            self.sleep(10)

        # magentaprint("Stopping rest for health",False)

    def update_aura(self, force=False):
        aura_updated = False

        if (force and time.time() > (self.aura_timer + 30)) or time.time() > (self.aura_timer + self.aura_refresh):
            if self.stopping or self.character.ACTIVELY_MAPPING:
                magentaprint("GrindThread.update_aura() returning false", False)
                aura_updated = False
            elif self.inventory.has_aura_pot():
                magentaprint("I have show aura pots so I'ma use these over mana", False)
                use_pot = ""
                for pot in self.inventory.aura_pot:
                    if self.inventory.has(pot):
                        use_pot = self.inventory.get_reference(pot)
                        break
                aura_updated = self.update_aura_with_pot(use_pot)

            elif Spells.showaura in self.character.spells:
                aura_updated = self.update_aura_with_spell()
        else:
            magentaprint("Last aura update %d seconds ago." % round(time.time() - self.aura_timer))
        
        if aura_updated:
            self.aura_timer = time.time()

        return aura_updated

    def update_aura_with_spell(self):
        cur_aura = self.character.AURA
        self.cast.update_aura(self.character)

        if not self.cast.success:  # Probably no mana since spell fail gets spammed
            return False
        else:
            self.character.AURA = self.cast.aura
            self.character.aura_check_count += 1
            updated_aura = self.character.AURA
            if str(cur_aura) != str(updated_aura):
                self.aura_updated_hook()
            
            return True

    def update_aura_with_pot(self, item):
        cur_aura = self.character.AURA
        self.cast.update_aura(self.character, item)

        if not self.cast.success:  # Probably no mana since spell fail gets spammed
            return False
        else:
            self.character.AURA = self.cast.aura
            self.character.aura_check_count += 1
            updated_aura = self.character.AURA
            if str(cur_aura) != str(updated_aura):
                self.aura_updated_hook()
            
            return True

    def heal_up(self):
        magentaprint("In heal_up.")
        C = self.character
        heal_cost = 2

        if self.stopping:
            return
        if self.has_ideal_health():
            return

        self.do_heal_skills()

        if self.has_ideal_health():
            return

        if not self.character.info.pty < 10:
            if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
                self.cast.cast('v')
                self.cast.wait_for_flag()

                if self.has_ideal_health():
                    return

                self.cast.start_thread('v')

        self.character.HAS_RESTORE_ITEMS = False # Restore items disabled?

        while BotThread.should_heal_up(
            self.character.HEALTH, self.character.HEALTH_TO_HEAL, self.character.MANA, heal_cost, self.character.KNOWS_VIGOR, self.character.HAS_RESTORE_ITEMS\
            ) and not self.stopping:

            self.do_heal_skills()
            # self.use_restorative_items() #spam them!!!

            if self.engage_any_attacking_mobs():
                if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
                    self.cast.start_thread('v')

            self.sleep(0.05)

        self.cast.stop()

    def buff_up(self):
        if self.stopping:
            return
        # self.do_buff_skills()
        if BotThread.can_use_timed_ability(self.character.LAST_BUFF, 180):
            self.use_buff_items()
            self.character.LAST_BUFF = time.time()

    def use_buff_ability(self):
        magentaprint("GrindThread.use_buff_ability()")
        return self.do_buff_skills()

    def use_buff_items(self):
        if self.inventory.has("milky potion"):
            self.command_handler.process('drink milky')
        if self.inventory.has("steel bottle"):
            self.command_handler.process('drink steel')

    def use_extra_bless_item(self):
        magentaprint("GrindThread.use_extra_bless_item()")
        if self.inventory.count('milky potion') + self.inventory.count('silver chalice') > 3:
            if self.inventory.has('milky potion'):
                self.command_handler.use.execute(self.inventory.get_first_reference('milky potion'))
            else:
                self.command_handler.use.execute(self.inventory.get_first_reference('silver chalice'))
            self.command_handler.use.wait_for_flag()

    def use_extra_steel_bottle(self):
        magentaprint("GrindThread.use_extra_steel_bottle()")
        if self.inventory.count('steel bottle') > self.character.steel_bottle_keep_amount:
            self.command_handler.use.execute(self.inventory.get_first_reference('steel bottle'))
            self.command_handler.use.wait_for_flag()

    def use_restorative_items(self):
        if self.inventory.has("small restorative"):
            self.command_handler.process('drink restorative')
            # large restorative
        elif self.inventory.has("small flask"):
            self.command_handler.process('drink small')
        elif self.inventory.has("white potion"):
            self.command_handler.process('drink white')
        elif self.inventory.has("scarlet potion"):
            self.command_handler.process('drink scarlet')
        elif self.inventory.has("large restorative"):
            self.command_handler.process('drink restorative')
        elif self.inventory.has("gold chased whiskey flask"):
            self.command_handler.process('drink chased')
            # white potion
        else:
            self.character.HAS_RESTORE_ITEMS = False

    def do_checks(self):
        self.check_weapons()

    def can_find_path(self):
        # if we can find the way to Chapel self.healing_area then we should be able to path anywhere
        # so we'll just check that we're not in the Chapel and that we can find the way to it
        if self.character.AREA_ID == 2:
            return True
        
        directions = self.mud_map.get_path(self.character.AREA_ID, 2)
        return directions != []

    def check_weapons(self):
        magentaprint('check_weapons()')
        # w = WeaponBot(self.char, self.command_handler, self.mrh, self.map)
        # w.repair_or_replace_weapon()
        if not self.stopping and not self.is_character_class('Mon') and not self.is_character_class('Mag'):
            magentaprint("Checking weapons for " + self.character._class.id,False)
            self.command_handler.weapon_bot.check_weapons()

    def check_armour(self):
        if self.stopping or self.is_character_class('Mon') or self.is_character_class('Mag'):
            return
        
        if self.can_find_path():
            self.command_handler.armour_bot.suit_up()

        # if not self.smartCombat.broken_weapon:
        #     return True

        # possible_weapons = self.decide_possible_weapons()

        # if not possible_weapons:
        #     magentaprint("check_weapons() couldn't find level 1 weapon.")
        #     self.pause()

        # magentaprint('check_weapons() possible weapons: ' + str(possible_weapons))

        # if self.smartCombat.try_weapons([w.to_string() for w in possible_weapons]):
        #     return True

        # if self.smartCombat.to_repair:
        #     pass

        # # if not self.go_purchase_item_by_type('weapon', self.character.weapon_type, self.character.weapon_level):
        # possible_weapons[0].map()

        # if self.go_purchase_item(possible_weapons[0]):
        #     magentaprint("check_weapons stacked shop path and dobuy onto purchase path, returning.")
        #     return True
        #     # if self.smartCombat.try_weapon(possible_weapons[0].name):  # I can't wield because I don't have the weapon yet.
        #     #     return True
        #     # else:
        #     #     magentaprint("Check weapons had trouble wielding bought weapon.")
        #     #     self.pause()
        # else:
        #     magentaprint("No weapon error - couldn't find anything in inventory or repair or shop...")
        #     self.pause()

        # return False

    def decide_possible_weapons(self):
        possible_weapons = []
        level = self.character.weapon_level

        while not possible_weapons and level > 0:
            magentaprint("check_weapons() trying lower level weapons.")
            possible_weapons = list(MudItem.get_suitable_item_of_type('weapon', self.character.weapon_type, level).values())
            level = level - 1

        return possible_weapons

    def go_purchase_item(self, item):
        magentaprint("GrindThread.go_purchase_item() got location id: " + str(item.get_purchase_location_id()))
        if item.get_purchase_location_id():
            self.direction_list = ["areaid%s" % item.get_purchase_location_id(), "dobuy%s" % item.to_string(), self.healing_area]
            return True
        else:
            return False

    def go_purchase_item_by_name(self, name):
        places = AreaStoreItem.get_by_name(name)
        magentaprint("GrindThread going to buy " + str(places))

        self.direction_list = ["areaid%s" % places.values()[0] , "dobuy%s" % name, self.healing_area]  # Something like Thatt

    def go_purchase_item_by_type(self, model, data, level):
        # Model is main item type (weapon, s-armor, consumable), Data is sub-type (Blunt, Body, etc)
        magentaprint('go_purchase_item_by_type() model: ' + str(model) + ', data: ' + str(data) + ', level: ' + str(level))
        suitable_weapons = MudItem.get_suitable_item_of_type(model, data, level)

        while not suitable_weapons and level >= 0 and not self.stopping:
            # Got nothing from db, so try lower level items
            level = level - 1
            suitable_weapons = MudItem.get_suitable_item_of_type(model, data, level)

        if not suitable_weapons:
            return False

        direction_list = []
        # self.character.MONSTER_KILL_LIST = []
        weapon = None

        for itemdict in suitable_weapons:
            # Use the first weapon that fits the model/data/level criteria
            weapon = suitable_weapons[itemdict]
            areaid = itemdict
            break

        magentaprint('go_purchase_item_by_type() chose ' + str(weapon))

        if weapon is not None:
            direction_list = ["areaid%s" % areaid]
            direction_list.append("dobuy%s" % weapon.obj.name)

        self.direction_list = direction_list

        return True

    def stop(self):
        super().stop()
        self.command_handler.armour_bot.stop()
        self.command_handler.weapon_bot.stop()

    def sell_items(self):
        if self.stopping:
            return

        # self.inventory.sell_stuff()
        # This is too much authority for Inventory, but this is also not a job for grind thread.
        # Time to make a mini bot (?) to support human Sel

        # self.inventory.get_inventory()  # Unnecessary if inventory is well tracked

        # for item_ref in self.sellable():
        #     if not self.__stopping:
        #         self.sell(item_ref)
        #     else:
        #         return
        # Ok we got it
        self.command_handler.sell_bot.sell_stuff()
        # Should this really be Grindthread though
        # There should be a puppet master that chooses between grinding and selling, I think

    def item_was_sold(self):
        # TODO: class Sell(Command)  - Get rid of these all caps flag variables and copypasta polling code
        magentaprint("GrindThread item_was_sold deprecated! use command_handler.sell.wait()")
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
        # self.inventory.drop_stuff()
        # This should maybe be a mini bot...
        # self.drop_refs(self.inventory.sellable())
        # self.drop_refs(self.inventory.droppable())
        self.command_handler.sell_bot.drop_stuff()
        # We also have broken rings...

    def drop_refs(self):
        pass

    def decide_which_mob_to_kill(self, monster_list):
        m_list = [str(m) for m in monster_list]


        # guard_count = 0
        for mob in m_list:
            if (self.character.level < 15 and re.search('town guard', mob)) or \
                re.search('town crier', mob) or \
               re.search('clown', mob) or \
               re.search('Rancher Plover', mob) or \
               re.search('bouncer', mob):
                return ''
            
            # if re.search('town guard', mob) and self.character.level < 14:
            #     return ''
            # low level characters fight market officials - there is an edge case here where they'll end up attacking Alaran and die
            if self.character.level < 11:
                if re.search('Alaran the Market Manager', mob):
                    return ''

        # if guard_count > 1:
        #     return ''
                

        if self.character.mobs.chase and self.character.mobs.chase in self.character.mobs.list:
            # Issue: Directions get pushed, but the bot tries to hit the juggler again after it's gone.
            # 1 Push the directions, leave it in mobs.attacking, remove it from mobs.list
            # 2 Stop killing things and chase
            # 3 do_regular_actions checks mobs.attacking first
            # 4 mobs.attacking only gets emptied if the bot engaged and the mobs in it and combat ended
            # - step 2 only works if nothing else is attacking...  step 2 should be kill everthing in mobs.attacking that hasn't run
            # hmph.  Quick fix - just don't hit mobs that aren't in mobs.list
            # This means the chase is low priority.
            mob = self.character.mobs.chase
            self.character.mobs.chase = ''
            self.character.mobs.chase_exit = ''
            return mob


        # loop through mobs
        # if mob is in the kill list then
        # if it's weak fight it
        # if it's tough then check if we have enough juice to fight it
        # if not then let's skip it for now
        for mob in m_list:
            if self.should_kill_mob(mob):
                return mob

        return ''


    def should_kill_mob(self, mob):
        return mob in self.character.MONSTER_KILL_LIST

    def do_buff_skills(self):
        if self.stopping:
            return
        # buff_skills hasn't been maintained - there are new ways to do this
        magentaprint("GrindThread.do_buff_skills() skill array length: " + str(len(self.character._class.buff_skills)))
        for skill in self.character._class.buff_skills:
            if skill.up():
                skill.execute()
                skill.wait_for_flag()
                return skill.success

    def do_combat_skills(self, target):
        for skill in self.character._class.slow_combat_skills:
            if skill.up():
                skill.execute(target)
                skill.wait_for_flag()
                return skill.success
        return False

    def do_heal_skills(self):
        for skill in self.character._class.heal_skills:
            if skill.up():
                skill.execute()
                skill.wait_for_flag()
                return skill.success
        return False

    def should_set_nervous_mode(self, target):
        magentaprint("GrindThread.should_set_nervous_mode() target: " + str(target), False)
        nervousmode = False
        if target == 'Choorga':
            nervousmode = True
        
        return nervousmode

    def engage_monster(self, monster):
        start_combat = get_timeint()
        self.character.STATE = 'in combat'
        self.kill.wait_until_ready()
        self.cast.wait_until_ready()

        if self.stopping:
            return

        C = self.character

        # if the monster name starts with "the" then it has been parsed incorrectly and that needs ot be stripped
        if monster.lower().startswith('the '):
            monster = monster[4:]

        # self.smartCombat.target = monster
        magentaprint("GrindThread engage_monster get_first_reference({0})".format(monster))
        new_target = self.character.mobs.list.get_first_reference(monster)
        # So... suppose someone (Qerp) runs by and kills the nobleman we have chased
        # Ok a fixed that up a level
        # I think we are assuming here that the target is in the list

        if new_target:
            self.smartCombat.engage_target(new_target, monster)
        else:
            # ie. dark room
            if len(monster.split(' ')) > 1:
                self.smartCombat.engage_target(str(monster).split(' ')[0], monster)
            else:
                self.smartCombat.engage_target(str(monster), monster)

        self.smartCombat.spell = self.smartCombat.favourite_spell
        nervousmode = self.should_set_nervous_mode(new_target)

        if nervousmode:
            magentaprint("Nervous mode engaged!", False)
            self.smartCombat.nervous_mode = True

        self.smartCombat.run()
        self.smartCombat.nervous_mode = False
        # What about flee... can we rest after a flee maybe, or quit...
        # Do lowest risk at this point, right... or do we want to rest
        # If the mob isn't there... better remove it from the lists
        # Ok it might not BE in the list (we chase, we call engage monster on the target we assume is there...)
        # Here is a good place to check smartCombat.fleeing... smartCombat.escape is blocking call with a bit of a sleep
        # Ok this really is the place to add some smarts
        if self.character.mobs.chase != '' and self.character.mobs.chase_exit != '':
            magentaprint("GrindThread.engage_monster() chasing mob, pushing onto direction list!")
            if self.character.AREA_ID is not None:
                # We can't assume it'll work here - we have to check to see if it'll work.
                magentaprint(str(self.mud_map.los_map[self.character.AREA_ID]))
                # magentaprint(str(self.mud_map.los_map[self.character.AREA_ID].edges(data=True)))  # dict object has no attribute 'edges'
                # magentaprint(str(self.mud_map.los_map[self.character.AREA_ID].edges()))

                # chase_aid = self.mud_map.los_map[self.character.AREA_ID][self.character.chase_dir]
                # magentaprint('Current node will definitely have chase node as a neighbor: ' + str(chase_aid in self.mud_map.los_map.neighbors(self.character.AREA_ID)))
                # magentaprint('Chase node neighbors() should have current node: ' + str(self.character.AREA_ID in self.mud_map.los_map.neighbors(chase_aid)))
                # return_path = self.mud_map.get_path(chase_aid, self.character.AREA_ID)

                # Should be able to iterate through neighbors to find the one with our edge data (15: {'name': 'east'})
                # g.neighbors(n) or self.character.all_neighbors()
                # for n in neighbors:
                #    if c
                # use G.edges(nbunch) to get the edges adjacent to my node, and pick out the one with the right exit name, and follow it.

                # pdb.set_trace()
                # area_exits = self.mud_map.los_map.edges(self.character.AREA_ID)
                # magentaprint('GrindThread area_exits trying area_id to index area: ' + str(area_exit))
                # area_exits2 = self.mud_map.los_map.edges(self.mud_map.los_map[self.character.AREA_ID])
                # magentaprint('GrindThread area_exits longer way of getting edges, using whole node to index: ' + str(area_exit2))
                # area_exit = area_exits

                # return_path = self.
                # chase_aid = self.mud_map.next_node(self.character.AREA_ID, self.character.chase_dir)
                # return_path = self.mud_map.get_path(self.character.chase_dir, self.character.AREA_ID)

                # chase_aid = self.mud_map.next_node(self.character.AREA_ID, self.character.chase_dir)
                # magentaprint("Got chase id! " + str(chase_aid))

                try:
                    # chase_aid = self.mud_map.los_map[self.character.AREA_ID][self.character.chase_dir]
                    chase_aid = self.mud_map.next_node(self.character.AREA_ID, self.character.mobs.chase_exit)
                    magentaprint('engage_monster() chase_aid: ' + str(chase_aid))
                    # I need to find the edge - the area exit.
                    return_path = self.mud_map.get_path(chase_aid, self.character.AREA_ID)
                    magentaprint('engage_monster() return_path: ' + str(return_path))

                    if len(return_path) > 0:
                        magentaprint("GrindThread.engage_monster adding directions " + str([self.character.mobs.chase_exit] + return_path))
                        self.direction_list = [self.character.mobs.chase_exit, "tap"] + return_path + self.direction_list
                        # buffer necessary?
                except Exception:
                    magentaprint("GrindThread.engage_monster() cannot chase because we would then be lost.")
                    self.character.mobs.chase = ''
                    self.character.mobs.chase_exit = ''
            else:
                magentaprint("BotThread.engage_monster() area id is none, so go to chapel after chasing.", False)
                go_hook = self.healing_area
                self.direction_list.insert(0, go_hook)

            # self.go(self.character.chase_dir)
            # self.character.chase_dir = ""
            # self.character.chase_mob = ""
        elif self.smartCombat.error:
            magentaprint("GrindThread engage_monster caught bad target - remove from mobs.list, which is {0}".format(self.character.mobs.list))
            if self.character.mobs.list.get(new_target):
                self.character.mobs.list.remove_by_ref(new_target)
            # (Normally mobs.list will removed stuff from itself by noticing the mob die,
            # but "Attack What?" (smartCombat.error isn't going to trigger any removal)

        # #magentaprint("end of enage dir list: " + str(self.direction_list), False)

        # Commenting: a) Mobs now does it's own removal and b) MOBS_ATTACKING is deprecated
        # if monster in self.character.MOBS_ATTACKING:
        #     self.character.MOBS_ATTACKING.remove(monster)
        magentaprint("engage monster \"" + monster + ",\" in attacking list: " + str(monster in self.character.mobs.attacking))
        if monster in self.character.mobs.attacking:
            magentaprint("GrindThread doing cleanup on erroneous mobs.attacking list, removing " + monster)
            self.character.mobs.attacking.remove(monster)
            # Reason: if Mobs gets notified in the wrong order, smelly beggar gets added after it gets removed,
            # and I got a bad mobs.attacking... order has been fixed.
        
        end_combat = get_timeint()
        self.character.COMBAT_TIME += (end_combat - start_combat).total_seconds()

        if not self.character.mobs.attacking:
            self.get_items_if_weapon()

    # def do_flee_hook(self):
    #     self.stop()
    #     self.command_handler.user_flee()
    #     # We could do a blocking thing here to start a rest

    def get_all_loot_items(self): #named for improved findability
        self.command_handler.get.execute_and_wait('all')
        if self.command_handler.get.failed_to_get_items:
            self.character.NEEDS_TO_SELL = True
            self.command_handler.get.failed_to_get_items = False

    def get_items_if_weapon(self):
        if not self.character.NEEDS_TO_SELL or hasattr(self.smartCombat.weapon_bot, 'weapon') or self.is_character_class('Mon'):
            self.get_items()
        else:
            magentaprint("GrindThread leaving items behind since weapon is broken.", False)
            # This is an easy fix for "You can't carry any more." stopping the bot completely
            # (Weapon shatters - bot picks up a heavy stick - bot has trouble shopping)
            # The better fix that will come in with TopDownGrind is to go and sell/drop when it fails to buy something.
            # That's not an absolute fix though, so this one might be kept (leaving anything on the ground,) the other solution
            # could eventually cause the bot to get bogged down if it picks up a keep_list item after a weapon shatter

    def get_items(self):
        # self.command_handler.process('ga')
        self.get_all_loot_items()
        # self.command_handler.get.wait_for_flag()

        while self.command_handler.get.cant_carry and not self.stopping:
            magentaprint("GrindThread.get_items, number of steel bottles: " + str(self.inventory.count('steel bottle')))
            if self.inventory.count('steel bottle') > 1:
                # TODO: make an Ability for steel bottle (protection spell)
                self.command_handler.use.by_name('steel bottle')
                self.command_handler.use.wait_for_flag()
            # elif self.inventory.count_restoratives() > 6:
            #     # self.command_handler.potion_thread_handler.consume.healing_potion()
            #     # self.command_handler.potion_thread_handler.consume.wait_for_flag()
            #     self.command_handler.potion_thread_handler.consume.execute_and_wait()
            #     # if self.command_handler.use.error:
            #     if self.command_handler.potion_thread_handler.consume.error:
            #         # What is this inventory bug
            #         # What about drink error
            #         # Ooookkkk we put in consume.error so we don't loop infinitely
            #         # We also made sure that drink removes from inventory, also so we won't loop infinitely
            #         return
            else:
                # just leave it there
                return
            self.get_all_loot_items()
            

    def engage_mobs_who_joined_in(self):
        # while self.character.MOBS_JOINED_IN != []:
        #     self.engage_monster(self.character.MOBS_JOINED_IN[0])
        #     self.character.MOBS_JOINED_IN = self.character.MOBS_JOINED_IN[1:]
        #     self.get_items()
        while self.character.mobs.attacking:
            self.engage_monster(self.character.mobs.attacking[0])
            # self.character.mobs.attacking = self.character.mobs.attacking[1:]
            self.get_items_if_weapon()

    def engage_any_attacking_mobs(self):
        engaged = False

        # while self.character.MOBS_ATTACKING != []:
        while self.character.mobs.attacking != [] and not self.stopping:
            engaged = True
            self.engage_monster(self.character.mobs.attacking[0])

        if engaged:
            self.get_items_if_weapon()

        return engaged

    def ready_for_combat(self):
        # has_ideal_health = self.character.HEALTH >= self.character.HEALTH_TO_HEAL
        # has_ideal_mana = self.character.MANA >= self.character.MANA_TO_ENGAGE
        # magentaprint("GrindThread.ready_for_combat() has_ideal_health: " + str(has_ideal_health) + ", has_ideal_mana: " + str(has_ideal_mana), False)

        return self.character.HEALTH >= self.character.HEALTH_TO_HEAL and \
               self.character.MANA >= self.character.MANA_TO_ENGAGE and \
               ((hasattr(self.command_handler.weapon_bot, 'weapon') and \
               self.command_handler.weapon_bot.has_usable_weapon_in_inventory()) or \
               not self.character._class.needs_weapon)

        # return (self.has_ideal_health() and
        #         self.has_ideal_mana())

    def find_nearby_node(self, chase_from_aid):
        # This should help the bot find itself after a chase from TrackGrind.

        # The chase-from area id is given and is one node away.  However, we don't know the exit to take to return.
        # This bot wanders around until it finds the node it came from.  It'll follow normal grindy engagement rules.

        # We can assume the map doesn't work.
        magentaprint('GrindThread.find_nearby_node()')
        cur_aid = self.character.AREA_ID

    def pause(self):
        # Wait for server timeout, engaging any attacking mobs
        magentaprint("GrindThread pausing forever.")
        self.command_handler.process('rest')
        while not self.stopping:
            self.sleep(1)
            if self.engage_any_attacking_mobs():
                self.command_handler.process('rest')
                # Maybe subscribe to an event about mobs attacking

    def set_up_automatic_ring_wearing(self):
        """ Makes some BotReactions so that when MudReaderHandler sees us
        pick up a ring, we'll wear it."""
        # r = GenericBotReaction("(?s)You get .+? an? .+? ring((,.+?\.)|(\.))", self.command_handler, "wear all")  # Regex problem
        # self.mudReaderHandler.register_reaction(r)
        rwr=RingWearingReaction(self.command_handler.wear, self.character.inventory)
        # self.command_handler.wear.ring_wearing_reaction = rwr # Well we decided not to do it this way
        self.mudReaderHandler.register_reaction(rwr)
        #Todo: fix for case where there's ring mail in the inventory or multiple rings are dropped
