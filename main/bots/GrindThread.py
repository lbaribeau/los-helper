
import re
import pdb
from math import floor, ceil

from bots.BotThread import BotThread
from misc_functions import magentaprint
from reactions.BotReactions import GenericBotReaction
from reactions.ring_reaction import RingWearingReaction
from Exceptions import *
from comm import Spells
from db.MudItem import MudItem
from db.Mob import Mob
from mini_bots.bless_and_prot import BlessTimer, ProtTimer

class GrindThread(BotThread):
    def __init__(self, character, command_handler, mudReaderHandler, mud_map):
        super().__init__(character, command_handler, mudReaderHandler, mud_map)
        self.bless_timer = BlessTimer(command_handler.use, self.inventory)
        self.mudReaderHandler.add_subscriber(self.bless_timer)
        self.prot_timer = ProtTimer(command_handler.use, self.inventory)
        self.mudReaderHandler.add_subscriber(self.prot_timer)
        self.loot_threshold = 1  # the amount of loot to collect before selling

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
            # self.check_weapons()  TODO: shopping doesn't work everywhere
            self.check_armour()

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
        # self.stopping = False # This breaks the stop command
        if exit_str == "prepare":
            self.command_handler.process(exit_str)
            return True
        elif exit_str == "sell_items":
            self.sell_items()
            return True
        elif exit_str == "drop_items":
            self.drop_items()
            return True
        elif re.match("dobuy.+?", exit_str):
            return self.buy_and_wield(exit_str)
        elif exit_str == 'kill_guard':
            # Since guards have multiple levels, I don't want them in the kill list, so we can do it this way
            # if self.ready_for_combat() and 'guard' in str(self.character.mobs.list).split("' '"):
            if self.ready_for_combat() and self.character.mobs.list.get('guard'):
                self.engage_monster('guard') # We'll want to wait for kill/cast and maybe switch targets
                self.engage_any_attacking_mobs()
            else:
                magentaprint("Go hook: Did not fight guard.")
            return True
        elif exit_str == 'buy_potions':
            return self.potion_shopping()
        else:
            return super().do_go_hooks(exit_str) # does areaid[\d] pathfinding

    def potion_shopping(self):
        buy = self.command_handler.buy

        while self.inventory.count('misty potion') < 4 and not self.stopping:
            buy.execute_and_wait('misty')
            if buy.success:
                self.inventory.add('misty potion')
            else:
                magentaprint("Error buying misty potions!")
                return True

        while self.inventory.count('glowing potion') < 1 and not self.stopping:
            buy.execute_and_wait('glowing')
            if buy.success:
                self.inventory.add('glowing potion')
            else:
                magentaprint("Error buying glowing potion!")
                return True

        return True # Helps the go hook know to pop I think

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
            crash  # failed to buy weapon
            return False

    def wield(self, item):
        return self.smartCombat.try_weapon(item)

    def do_on_blocking_mob(self):
        self.engage_monster(self.character.GO_BLOCKING_MOB)
        self.character.GO_BLOCKING_MOB = ""
        self.engage_any_attacking_mobs()
        # self.check_weapons()  # TODO: shopping doesn't work everywhere

        if not self.character.BLACK_MAGIC:
            self.heal_up()

    def do_on_successful_go(self):
        super().do_on_successful_go()


    def do_regular_actions(self):
        # This is regular_actions hook is actually in a funny spot (maybe)
        # We want to wait for successful go before doing anything
        # I think that engaging enemies at this time can catch an enemy from the previous zone

        # There is a counter for "no exit", which is when the go target is invalid
        # If it maxes out then a contingency is triggered
        # super() also pops the direction list
        # All this used to be do_regular_actions

        # So in this part we need to do any steps prior to picking the target
        # We also want to be hitting all the targets we are interested in, and leaving at the appropriate time
        # This is mainly - do combat for one node

        C = self.character

        chase_ref = C.mobs.list.get_last_reference(C.mobs.chase)
        C.mobs.chase = ''  # It should be a chase list (no would be better to chase one at a time)
        C.mobs.chase_exit = ''

        if chase_ref:
            new_target = chase_ref # This is a reference, but the other clause hasn't made a reference yet
            # new_target = C.mobs.chase 
            self.engage_monster(new_target) # Need to make sure this gets removed from mobs.list

        if C.mobs.chase:
            return # it ran again (prioritize chasing over other attacking mobs I guess)
            # Keeps the chase list short if possible

        if C.mobs.attacking != [] and not self.ready_for_combat():
            return
            # Try leaving if we want to leave - then we'll get into any fights about blocking if necessary

        self.engage_any_attacking_mobs()

        # Now it seems like we are out of combat
        # If we got blocked... we might not get to this code... 
        self.maybe_do_heal_skills()
        if not C.BLACK_MAGIC:
            self.heal_up() # Hopefully this can handle attackers
        if self.stopping or C.mobs.chase:
            # Actually we want to finish our wait setup before chasing, right? No Go will do that
            return

        # Let's do any waiting we have to do before picking our next target, in case an angry kobold arrives
        # Hmmm... so we'll fight if it blocks us, but we can try to leave first, but that costs waiting both cooldowns
        self.smartCombat.wait_for_one_of_kill_and_cast()
        if self.ready_for_combat():
            self.engage_any_attacking_mobs()
        if self.stopping or C.mobs.chase:
            return
        self.smartCombat.wait_for_both_of_kill_and_cast()
        if self.ready_for_combat():
            self.engage_any_attacking_mobs()
        if self.stopping or C.mobs.chase:
            return

        # TODO: Ideally we interrupt if something arrives, for now I'm just avoiding fighting two at once 
        # Have an object that subscribes to mob attacks you and implements .clear() and .wait() (inherits threading.Event)
        # I guess you have to spawn a thread to do the sleep time part unless there's some other tool for that
        fresh_target = self.decide_which_mob_to_kill(C.mobs.list) 
        if fresh_target and self.ready_for_combat():
            self.engage_monster(fresh_target)
            # Why not just call do_regular_actions at this point (handles chasing and attackers)
            # Because it doesn't handle chasing, we need to return for that
            if self.ready_for_combat():
                self.engage_any_attacking_mobs()
            # I think we fight attackers here, so we don't have to wait for Go, and to catch a breather before chasing, right?
            # We could lose track if more things run though
            # We'll have the paths pushed but we'll forget we were fighting... (multiple runners) that's probably fine
            if C.mobs.chase:
                # Ack we need to do the combat wait setup before chasing right? No, Go will do that
                return
            else:
                self.do_regular_actions() # Does the wait setup and fights another fresh_target
        # else:

        # while fresh_target != "" and self.ready_for_combat() and not self.stopping and not C.mobs.chase:
        #     magentaprint("GrindThread fresh_target loop targeting: " + fresh_target + " then mobs joined in then any attacking.")
        #     # Ok let's do some wait - setup in case something arrives so we can switch targets
        #     # Always do wait setup before picking a new target - wait setup is waiting for cooldowns, and engaging any attackers
        #     self.engage_monster(fresh_target) # Need to make sure this gets removed from mobs.list
        #     self.engage_any_attacking_mobs()
        #     # self.check_weapons()  # TODO: shopping doesn't work everywhere
        #     # We could call this recursively actually... instead of while looping

        #     if not C.BLACK_MAGIC:
        #         self.heal_up()

        #     if self.ready_for_combat() and not C.mobs.chase:
        #         magentaprint("GrindThread picking a new target since " + fresh_target + " was defeated")
        #         new_target = self.decide_which_mob_to_kill(C.mobs.list)
        #     else:
        #         new_target = ""            

        # Old comments...
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

    def print_bot_stats(self):
        self.command_handler.inventory.execute_and_wait()
        self.command_handler.process('experience')
        # self.command_handler.process('aura')
        # self.command_handler.cast.print_aura_timer()
        magentaprint("Last target was " + str(self.smartCombat.target))
        self.command_handler.process('trackno')
        self.command_handler.process('time')

    def rest_and_check_aura(self):
        # This method is only efficient in a healing area
        magentaprint("GrindThread.rest_and_check_aura()")
       # self.command_handler.print_experience()
        self.print_bot_stats() # Display while resting

        if self.update_aura():
            # Most reasonable reason to fail is if we have no mana... fairly rare
            # Only update aura before resting, save that one mana and the cast cooldown time after resting
            # Idea: postpone a bit if it would mean another mana tick 
            # (or better, take a free cast if it wouldn't mean another mana tick)
            self.aura_updated_hook()
            # Ok resist the temptation to delay using the misty potion such that setting the timer is delayed
            # Instead just increase the refresh rate
            # Because there's no real difference between drinking the misty potion before or after resting
            # Maybe consider starting the timer after resting though to slightly improve the aura timing system.
            # ie. resting can take 10 minutes for some characters

        magentaprint("Health ticks needed: {}, Mana ticks needed: {}.".format(round(self.health_ticks_needed(), 1), round(self.mana_ticks_needed(), 1)))
        self.chapel_heal_up()
            # TODO: Keep track of when ticks are coming and how big they'll be, and avoid vigging
            # away all the mana for characters with low piety, whose vigors will not do much,
            # and may just be one tick away from good health.

        # if self.character.MANA < self.character.maxMP - 2*(self.character.mana_tick() + 2):
        if self.mana_ticks_needed() > 2.0:
            # MANA_TO_WAIT differentiates between hitting 'rest' and just hitting
            # 'enter' a bunch (waiting vs resting)
            self.rest_until_ready()
        elif self.character.MANA < self.mana_to_go:
            self.wait_for_mana()

        if self.character.level > 3 and self.character.maxMP > 10:
            self.heal_up() # I think that this assumed that we have piety
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
        # If too much hp, go fight to bring hp down*.  If too much mp, vig to balance.
        # After vigging and resting a full mana pool, hp may still not be very high,
        # and in that case, keep resting since benefits should be active.
        # *requires strong enemy for black magic users

        # Todo: don't stay if the chapel bonus isn't needed (2 mana, some hp)
        # ie. 18 int and need only 3 mana

        magentaprint("In chapel_heal_up.")
        C = self.character

        if self.stopping or C.HEALTH >= self.health_to_go:
            return

        self.do_heal_skills()
        # Todo: my guy isn't doing the enter trick to wait for one mana tick - he's just hitting rest

        # if C.HEALTH >= self.health_to_go or not any(s.startswith(Spells.vigor) for s in C.spells):
        if C.HEALTH >= self.health_to_go or Spells.vigor not in C.spells:
            return

        magentaprint("Health ticks needed: {}, Mana ticks needed: {}.".format(round(self.health_ticks_needed(), 1), round(self.mana_ticks_needed(), 1)))

        self.cast.wait_until_ready()
        vig       = 2
        # chapel    = 2 # additional hp tick amount
        # maxHP     = C.maxHP
        # maxMP     = C.maxMP
        # mana_tick = C.mana_tick()
        # while   (self.health_ticks_needed() > self.mana_ticks_needed() or
        #         C.MANA - (maxMP % mana_tick()+chapel) % (mana_tick()+chapel) >= 2) and (
        while   ceil(self.health_ticks_needed()) > ceil(self.mana_ticks_needed()) and \
                C.MANA >= vig                                                     and \
                not self.ready_for_combat()                                       and \
                not self.stopping:
                # C.mana_tick()+2 % C.maxMP - C.MANA > 2:
                # C.maxMP - C.MANA % C.mana_tick()+chapel - vig >= 0: #C.mana_tick() + vig - chapel:
                # Laurier does math!  (Mathing out whether we should vig or in the chapel)
            # magentaprint("Health ticks needed: " + str(round(self.health_ticks_needed(), 1)) + ", Mana ticks needed: " + str(round(self.mana_ticks_needed(), 1)))
            magentaprint("Health ticks needed: {}, Mana ticks needed: {}.".format(round(self.health_ticks_needed(), 1), round(self.mana_ticks_needed(), 1)))
            # Ehrm doesn't ready_for_combat need us to have a weapon...

            if self.do_heal_skills():
                continue
            # elif self.inventory.count_small_restoratives() > 5:
            #     self.command_handler.potion_thread_handler.consume.small_healing_potion_with_wait()
            elif self.maybe_use_extra_small_restoratives():
                # Hmmm, I used to save these things more
                continue
            else:
                # if self.engage_any_attacking_mobs():
                #     if BotThread.can_cast_spell(self.character.MANA, heal_cost, self.character.KNOWS_VIGOR):
                #         self.cast.start_thread('v')
                self.cast.cast('v')
                self.cast.wait_for_flag() # Wait in two segments because it's not guaranteed to have worked
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
        return (self.character.maxHP - self.character.HEALTH) / (self.character.hp_tick() + 3) # Confirmed chapel bonus is 3

    def mana_ticks_needed(self):
        # return (self.character.maxMP - self.character.MANA) / (self.character.mana_tick() + 2) # Chapel bonus is 2
        # There is a 1 mana bonus when resting not included
        # Seems like you get ONE OR TWO regular ticks and then the rest have a bonus mana on them
        # Assume one regular tick to make the math simpler
        C = self.character
        return (C.MANA < C.maxMP) + (C.maxMP-(C.MANA+C.mana_tick()+2))/(C.mana_tick()+3) # +3 is 2 from chapel and 1 from resting

    def rest_until_ready(self):
        magentaprint("Rest_until_ready(): hp ticks needed: {}, mana ticks needed: {}.".format(round(self.health_ticks_needed(), 1), round(self.mana_ticks_needed(), 1)))

        # Rest until one of hp or mp is maxed.  This way we aren't waiting for both.
        # Hopefully things are somewhat balanced.  If things are unbalanced, benefits
        # of resting can be used to balance, and if it's a shorter rest, then just go
        # when one of them is maxed (use ready_for_combat as a mimimum, if after resting
        # we aren't ready for combat, erhm, well that's kind of ridiculous.)

        # TODO: keep resting if benefitting from resting until maxed.

        if (self.neither_is_maxed or self.one_is_too_low) and not self.stopping:
            self.command_handler.process("rest")

        while (self.neither_is_maxed or self.one_is_too_low) and not self.stopping:
            if self.engage_any_attacking_mobs():
                self.command_handler.process("rest")
            self.sleep(0.1)

    @property
    def neither_is_maxed(self):
        return self.character.HEALTH < self.character.maxHP and self.character.MANA < self.character.maxMP

    @property
    def one_is_too_low(self):
        return self.character.HEALTH < self.health_to_go or self.character.MANA < self.mana_to_go

    def wait_for_mana(self):
        magentaprint("GrindThread.wait_for_mana(): hp ticks needed: {}, mana ticks needed: {}.".format(round(self.health_ticks_needed(), 1), round(self.mana_ticks_needed(), 1)))
        while self.character.MANA < self.mana_to_go and not self.stopping:
            for i in range(0,20):
                self.sleep(0.25)
                if self.stopping:
                    return
            self.engage_any_attacking_mobs()
            self.command_handler.prompt.clear()
            self.command_handler.process('')
            self.command_handler.prompt.wait()

    def rest_for_health(self):
        magentaprint("BotThread.rest_for_health()")

        if self.has_ideal_health():
            return

        self.do_heal_skills()
        self.command_handler.process("rest")
        # magentaprint(self.has_ideal_health(), False)

        while not self.has_ideal_health() and not self.stopping:
            magentaprint("GrindThread.rest_for_health() stopping is: " + str(self.stopping))
            if self.engage_any_attacking_mobs():
                self.command_handler.process("rest")
            elif self.do_heal_skills():
                self.command_handler.process("rest")

            self.sleep(1.2)

        # magentaprint("Stopping rest for health",False)

    def update_aura(self):
        # if self.stopping or self.character.ACTIVELY_MAPPING or not Spells.showaura in self.character.spells:
        # if self.stopping or self.character.ACTIVELY_MAPPING or not any(s.startswith(Spells.showaura) for s in self.character.spells):
        self.command_handler.process('aura')

        if self.stopping or self.character.ACTIVELY_MAPPING or not self.cast.check_aura_timer():
            return False

        if self.inventory.has('misty potion'):
            # self.command_handler.use.execute_and_wait(self.inventory.get_first_reference('misty potion'))
            self.command_handler.use.execute(self.inventory.get_first_reference('misty potion'))
            self.command_handler.cast.clear()
            self.command_handler.cast.wait_for_flag() # Prefer to matches the aura text? Should unset cast's flag first
            return self.command_handler.use.success
                # Cast will update the timer automatically
                # return True

        if Spells.showaura in self.character.spells:
            self.cast.update_aura(self.character)
            return self.cast.success # Could be no mana since spell fail gets spammed

        return False

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
        C = self.character
        heal_cost = 2

        # Ideal means sufficient here
        if self.has_ideal_health() or self.stopping:
            return

        self.do_heal_skills()

        if self.has_ideal_health() or self.stopping:
            return

        self.maybe_use_extra_small_restoratives() # These would probably get tossed and we can rely on scarlets for safety

        if self.has_ideal_health() or self.stopping:
            return

        if BotThread.can_cast_spell(C.MANA, heal_cost, C.KNOWS_VIGOR):
            self.cast.cast('v')
            self.cast.wait_for_flag()

            if self.has_ideal_health() or self.stopping:
                return

            self.cast.start_thread('v')

        C.HAS_RESTORE_ITEMS = False # Restore items disabled?

        while BotThread.should_heal_up(
            C.HEALTH, C.HEALTH_TO_HEAL, C.MANA, heal_cost, C.KNOWS_VIGOR, C.HAS_RESTORE_ITEMS\
            ) and not self.stopping:
            self.do_heal_skills()
            if self.engage_any_attacking_mobs():
                if BotThread.can_cast_spell(C.MANA, heal_cost, C.KNOWS_VIGOR):
                    self.cast.start_thread('v')
            #self.use_restorative_items() #spam them!!!
            self.sleep(0.05)

        self.cast.stop()

    def buff_up(self):
        if self.stopping:
            return
        self.do_buff_skills()
        if BotThread.can_use_timed_ability(self.character.LAST_BUFF, 180):
            self.use_buff_items()
            self.character.LAST_BUFF = time.time()

    def use_buff_ability(self):
        magentaprint("GrindThread.use_buff_ability()")
        return self.do_buff_skills()

    def use_buff_items(self):
        if self.inventory.has("milky potion"):
            self.command_handler.process('drink milky')
        elif self.inventory.has("steel bottle"):
            self.command_handler.process('drink steel')
        else:
            self.character.HAS_BUFF_ITEMS = False

    def use_extra_bless_item(self):
        magentaprint("GrindThread.use_extra_bless_item()")
        if self.inventory.count('milky potion') + self.inventory.count('silver chalice') > 3:
            if self.inventory.has('milky potion'):
                self.command_handler.use.execute_and_wait(self.inventory.get_first_reference('milky potion'))
            else:
                self.command_handler.use.execute_and_wait(self.inventory.get_first_reference('silver chalice'))
            # self.command_handler.use.wait_for_flag()

    def use_extra_steel_bottle(self):
        magentaprint("GrindThread.use_extra_steel_bottle()")
        if self.inventory.count('steel bottle') > self.character.steel_bottle_keep_amount:
            self.command_handler.use.execute_and_wait(self.inventory.get_first_reference('steel bottle'))
            # self.command_handler.use.wait_for_flag()

    def use_restorative_items(self):
        if self.inventory.has("small restorative"):
            self.command_handler.process('drink restorative')
            # large restorative
        elif self.inventory.has("scarlet potion"):
            self.command_handler.process('drink scarlet')
        elif self.inventory.has("tree root"):
            self.command_handler.process('eat root')
            # white potion
        else:
            self.character.HAS_RESTORE_ITEMS = False

    def check_weapons(self):
        magentaprint('check_weapons()')
        # w = WeaponBot(self.char, self.command_handler, self.mrh, self.map)
        # w.repair_or_replace_weapon()
        if not self.stopping:
            self.command_handler.weapon_bot.check_weapons()

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
            # Could use level_max for that

        return possible_weapons

    def go_purchase_item(self, item):
        magentaprint("GrindThread.go_purchase_item() got location id: " + str(item.get_purchase_location_id()))
        if item.get_purchase_location_id():
            self.direction_list = ["areaid%s" % item.get_purchase_location_id(), "dobuy%s" % item.to_string(), "areaid2"]
            return True
        else:
            return False

    def go_purchase_item_by_name(self, name):
        places = AreaStoreItem.get_by_name(name)
        magentaprint("GrindThread going to buy " + str(places))

        self.direction_list = ["areaid%s" % places.values()[0] , "dobuy%s" % name, "areaid2"]  # Something like Thatt

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

    def check_armour(self):
        if self.stopping:
            return
        self.command_handler.armour_bot.suit_up()

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

    def maybe_use_extra_small_restoratives(self):
        use=self.command_handler.use
        # self.command_handler.potion_thread_handler.result=''
        use.result=''
        while self.character.HEALTH < self.character.info.maxHP and \
            ceil(self.health_ticks_needed()) > ceil(self.mana_ticks_needed()) and \
            not self.stopping and \
            self.command_handler.potion_thread_handler.consume.small_healing_potion_with_wait():
            pass
            # This'll exit if we run out of small potions
            # Note that these ticks_needed functions are neglecting a bonus 1 mana when resting kicks in
        return use.success
        # return self.command_handler.potion_thread_handler.consume.success
        # We are just trying to use potions that we would otherwise drop

        # while self.character.HEALTH < self.character.info.maxHP:
        #     for i in ['chicken soup', 'small restorative', 'white potion']:
        #         if i not in self.inventory.keep_list:
        #             r = self.inventory.get_first_reference(i)
        #             if r:
        #                 self.command_handler.use.execute_and_wait(r)
        #                 # break # Hmmm... it only used one restorative
        #                 continue
        #             # idea - white amulet - 3 second cooldown
        #     break # Ok I see why... we break out here without checking for more restoratives

        # use = self.command_handler.use
        # small_restoratives = ['chicken soup', 'small restorative', 'white potion']
        # while self.character.HEALTH < self.character.info.maxHP and self.inventory.has_any(self.small_restoratives):
        #     for i in self.small_restoratives:
        #         while not self.stopping:
        #             r = self.inventory.get_first_reference(i)
        #             if r:
        #                 # use.execute_and_wait(r)
        #                 # while use.please_wait1 and not self.stopping:
        #                 #     # Persistent execute?
        #                 #     use.execute_and_wait(r)
        #                 use.wait_until_ready() # Persistent is less necessary with this
        #                 use.persistent_execute(r) # Handles please wait 1 more second if we are spamming small restoratives
        #                 # (note that use has a cooldown and supports wait_until_ready())
        #                 if not use.success:
        #                     print('\a')
        #                     raise
        #                 # This may not be optimal - could be over using them when we will be waiting for mana
        #             else:
        #                 break

        # Rewrite this again...
        # Seems like this isn't checking the HP clause enough
        # while ceil(self.health_ticks_needed()) < ceil(self.mana_ticks_needed()) and self.inventory.has_any(self.small_restoratives) and not self.stopping and self.consume.small_healing_potion_with_wait():
        #     pass

    def drop_items(self):
        self.maybe_use_extra_small_restoratives()

        # self.inventory.drop_stuff()
        # This should maybe be a mini bot...
        # self.drop_refs(self.inventory.sellable())
        # self.drop_refs(self.inventory.droppable())
        self.command_handler.sell_bot.drop_stuff()
        # We also have broken rings...
        # Hmmmm, what if some of it is restoratives?

    def drop_refs(self):
        pass

    def decide_which_mob_to_kill(self, monster_list):
        C = self.character
        if C.mobs.chase:
            if C.mobs.chase in C.mobs.list:
                # Issue: Directions get pushed, but the bot tries to hit the juggler again after it's gone.
                # 1 Push the directions, leave it in mobs.attacking, remove it from mobs.list
                # 2 Stop killing things and chase
                # 3 do_regular_actions checks mobs.attacking first
                # 4 mobs.attacking only gets emptied if the bot engaged and the mobs in it and combat ended
                # - step 2 only works if nothing else is attacking...  step 2 should be kill everthing in mobs.attacking that hasn't run
                # hmph.  Quick fix - just don't hit mobs that aren't in mobs.list
                # This means the chase is low priority.
                mob = C.mobs.chase
                C.mobs.chase = ''
                C.mobs.chase_exit = ''
                # return mob
                return C.mobs.list.get_last_reference(mob) # Assume it's the last one
                # Ummm we want to make sure we follow it then fight it (not a mob with the same name in the current node)
                # So don't fight the next mob if chase is set
                # Hmmm maybe this'll work
                # It's possible the chased mob could be killed
                # So we gotta unset chase at some point
                # Well we should be chasing right away
                # So we can unset it right here on the first call? 
                # No we have to return '' so we don't fight the next mob - maybe do that at the caller level
                # (Check chase, if chase is set, don't be deciding what to kill)
                # Ok there is already more chase code in regular_actions and chase does get unset
                # We shouldn't get called here if chase is set
            else:
                magentaprint("decide_which_mob_to_kill assuming we have something to chase!")
                return '' # Is it possible we won't find the chased mob? As soon as we get to a new node we have to unset chase

        m_list = [str(m) for m in monster_list]

        for mob in m_list:
            if re.search('town guard', mob) or \
               re.search('town crier', mob) or \
               re.search('clown', mob) or \
               re.search('bouncer', mob):
                return ''

        blue_mobs = [
            'acolyte','vicar','robed pilgrim','penitent','young knight','lay priest','protector','battered knight','orange picker','robed priest','priest'
        ]

        for mob in m_list:
            if mob in C.MONSTER_KILL_LIST and (mob not in blue_mobs or not self.cast.aura or self.cast.aura >= C.preferred_aura):
                return mob
                # We can add in robed pilgrim if we want and other blue things... with this code in place

        return ''

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
                skill.execute_and_wait()
                return skill.success
        return False

    def maybe_do_heal_skills(self):
        for skill in self.character._class.heal_skills:
            if skill.up() and self.character.HEALTH < self.character.maxHP-skill.max_amount-self.character.hp_tick():
                skill.execute_and_wait()
                return skill.success
        return False



    def engage_monster(self, monster):
        # Here, monster is GIVEN
        # Anything that can happen to change the target should be done by now
        # By extension, that means that, we are ready to fight (kill and cast are ready)

        # Idea: if not ready, try using some spare restoratives

        C = self.character
        SC = self.smartCombat

        # if C.mobs.attacking == []:
        #     SC.wait_for_one_of_kill_and_cast()
        # if C.mobs.attacking == []:
        #     SC.wait_for_both_of_kill_and_cast() # TODO: Ideally we interrupt if something arrives, for now I just want to attack the right thing
        
        if C.mobs.attacking == []:
            # self.kill.wait_until_ready()
            # self.cast.wait_until_ready()
            # Problem: an angry kobold just showed up
            # So: wait for the first one of kill / cast
            # Can we switch mobs at this point? Fair enough right?
            # Maybe do some checks up a level
            # So, how about we call engage_any_attacking_mobs before engage_monster, and we also do the waits outside of this scope
            # We could do it here... maybe

            if C.HEALTH == C.maxHP and \
               C.MANA == C.maxMP and \
               self.bless_timer.check_timer() and \
                self.prot_timer.check_timer():
                self.bless_timer.maybe_bless()
                self.prot_timer.maybe_prot()
                # Could do buff ability here
                # Casts of show aura can cause it not to buff like this
                # Idea - don't buff if on pawn/tip path or repairing

        if self.stopping:
            return

        magentaprint("GrindThread engage_monster get_first_reference({0})".format(monster))
        new_target = C.mobs.list.get_first_reference(monster)
        # So... suppose someone (Qerp) runs by and kills the nobleman we have chased
        # Ok, fixed that up a level
        # I think we are assuming here that the target is in the list

        if new_target:
            SC.target = new_target
        else:
            # ie. dark room
            if len(monster.split(' ')) > 1:
                SC.target = str(monster).split(' ')[0]
            else:
                SC.target = str(monster)
            # Hmmm what if it wandered away??
            # Some of this could be moved up to regular actions
            # What we could do here is, check that the mob is here, wait up, then check again

        mob_level = Mob.get_mob_level_by_name(monster)

        if mob_level:
            if mob_level >= 12 and Spells._get_level_3(SC.favourite_spell) in C.spells:
                SC.spell = Spells._get_level_3(SC.favourite_spell)
            elif mob_level >= 8 and Spells._get_level_2(SC.favourite_spell) in C.spells:
                SC.spell = Spells._get_level_2(SC.favourite_spell)
            else:
                SC.spell = SC.favourite_spell
        else:
            SC.spell = SC.favourite_spell

        SC.run() # we recently got rid of waits, maybe that's why SC exits
        # What about flee... can we rest after a flee maybe, or quit...
        # Do lowest risk at this point, right... or do we want to rest
        # If the mob isn't there... better remove it from the lists
        # Ok it might not BE in the list (we chase, we call engage monster on the target we assume is there...)
        # Here is a good place to check smartCombat.fleeing... smartCombat.escape is blocking call with a bit of a sleep
        # Ok this really is the place to add some smarts
        # Here we are initiating a chase... it'd be nice to prioritize that over starting a new fight
        # Also need to support... if we get blocked I believe
        # We could end up with two chases then if we are getting blocked
        if C.mobs.chase != '' and C.mobs.chase_exit != '':
            magentaprint("GrindThread.engage_monster() chasing mob, pushing onto direction list!")
            if C.AREA_ID is not None:
                # We can't assume it'll work here - we have to check to see if it'll work.
                magentaprint(str(self.mud_map.los_map[C.AREA_ID]))
                # magentaprint(str(self.mud_map.los_map[C.AREA_ID].edges(data=True)))  # dict object has no attribute 'edges'
                # magentaprint(str(self.mud_map.los_map[C.AREA_ID].edges()))

                # chase_aid = self.mud_map.los_map[C.AREA_ID][C.chase_dir]
                # magentaprint('Current node will definitely have chase node as a neighbor: ' + str(chase_aid in self.mud_map.los_map.neighbors(C.AREA_ID)))
                # magentaprint('Chase node neighbors() should have current node: ' + str(C.AREA_ID in self.mud_map.los_map.neighbors(chase_aid)))
                # return_path = self.mud_map.get_path(chase_aid, C.AREA_ID)

                # Should be able to iterate through neighbors to find the one with our edge data (15: {'name': 'east'})
                # g.neighbors(n) or c.all_neighbors()
                # for n in neighbors:
                #    if c
                # use G.edges(nbunch) to get the edges adjacent to my node, and pick out the one with the right exit name, and follow it.

                # pdb.set_trace()
                # area_exits = self.mud_map.los_map.edges(C.AREA_ID)
                # magentaprint('GrindThread area_exits trying area_id to index area: ' + str(area_exit))
                # area_exits2 = self.mud_map.los_map.edges(self.mud_map.los_map[C.AREA_ID])
                # magentaprint('GrindThread area_exits longer way of getting edges, using whole node to index: ' + str(area_exit2))
                # area_exit = area_exits

                # return_path = self.
                # chase_aid = self.mud_map.next_node(C.AREA_ID, C.chase_dir)
                # return_path = self.mud_map.get_path(C.chase_dir, C.AREA_ID)

                # chase_aid = self.mud_map.next_node(C.AREA_ID, C.chase_dir)
                # magentaprint("Got chase id! " + str(chase_aid))

                try:
                    # chase_aid = self.mud_map.los_map[C.AREA_ID][C.chase_dir]
                    chase_aid = self.mud_map.next_node(C.AREA_ID, C.mobs.chase_exit)
                    magentaprint('engage_monster() chase_aid: ' + str(chase_aid))
                    # I need to find the edge - the area exit.
                    return_path = self.mud_map.get_path(chase_aid, C.AREA_ID)
                    magentaprint('engage_monster() return_path: ' + str(return_path))

                    if len(return_path) > 0:
                        magentaprint("GrindThread.engage_monster adding directions " + str([C.mobs.chase_exit] + return_path))
                        self.direction_list = [C.mobs.chase_exit] + return_path + self.direction_list
                        # buffer necessary?
                except Exception:
                    magentaprint("GrindThread.engage_monster() cannot chase because we would then be lost.")
                    C.mobs.chase = ''
                    C.mobs.chase_exit = ''
            else:
                magentaprint("BotThread.engage_monster() area id is none, so go to chapel after chasing.")
                go_hook = "areaid2"
                self.direction_list.insert(0, go_hook)

            # self.go(C.chase_dir)
            # C.chase_dir = ""
            # C.chase_mob = ""
        elif SC.error:
            magentaprint("GrindThread engage_monster SC error (bad target) - remove from mobs.list and attacking: {} {}".format(C.mobs.list, C.mobs.attacking))
            if C.mobs.list.get(new_target):
                C.mobs.list.remove_by_ref(new_target)
            if monster in C.mobs.attacking:
                C.mobs.attacking.remove(monster)
            # (Normally mobs.list will remove stuff from itself by noticing the mob die,
            # but "Attack What?" (smartCombat.error isn't going to trigger any removal)

        # #magentaprint("end of enage dir list: " + str(self.direction_list), False)

        # Commenting: a) Mobs now does it's own removal and b) MOBS_ATTACKING is deprecated
        # if monster in C.MOBS_ATTACKING:
        #     C.MOBS_ATTACKING.remove(monster)
        magentaprint("Ending engage monster \"" + monster + ",\" in attacking list: " + str(monster in C.mobs.attacking))
        if monster in C.mobs.attacking:
            # magentaprint("GrindThread doing cleanup on erroneous mobs.attacking list, removing " + monster)
            # C.mobs.attacking.remove(monster)
            # Reason: if Mobs gets notified in the wrong order, smelly beggar gets added after it gets removed,
            # and I got a bad mobs.attacking... order has been fixed.
            # PROBLEM: Bot removes bandit guard here when it's actually attacking! (TODO)
            # Ok the only check was if monster in attacking... since it was two bandit guards we got into this case
            # (Bot falls through into GO code which waits for cast to be ready when it should be attacking)
            # So.... is there a better way to fix the smelly beggar thing... oyyyyyy
            # So... the 2nd bandit guard is attacking, the bot removes it here wrongly, then goes into the travel loop,
            # which WAITS FOR CAST READY, so it messes up the combat against the second bandit guard for 7 seconds
            # (attack, cast 1.0 seconds later, it dies, then wait for cast ready 3.6 s, then go and get blocked)
            # So what if we dont' remove from mobs attacking... we might get missed attacks I guess? (start attacking at ghosts?)
            # Maybe 'Go" needs to take better control of this... ala TRYING_TO_MOVE
            magentaprint("Grindthread: Is something wrong with the attacking list??")
            # I guess we have to check somewhere (ie at the top of this function or in smart Combat) whether the target was good

        # if C.mobs.attacking == []:
        #     self.get_items_if_weapon()
        if not C.mobs.chase and not SC.error:
            self.get_items_if_weapon()

    # def do_flee_hook(self):
    #     self.stop()
    #     self.command_handler.user_flee()
    #     # We could do a blocking thing here to start a rest

    def get_items_if_weapon(self):
        if hasattr(self.smartCombat.weapon_bot, 'weapon'):
            self.get_items()
        else:
            magentaprint("GrindThread leaving items behind since weapon is broken.")
            # This is an easy fix for "You can't carry any more." stopping the bot completely
            # (Weapon shatters - bot picks up a heavy stick - bot has trouble shopping)
            # The better fix that will come in with TopDownGrind is to go and sell/drop when it fails to buy something.
            # That's not an absolute fix though, so this one might be kept (leaving anything on the ground,) the other solution
            # could eventually cause the bot to get bogged down if it picks up a keep_list item after a weapon shatter

    def get_items(self):
        # self.command_handler.process('ga')
        self.command_handler.get.execute_and_wait('all')
        # self.command_handler.get.wait_for_flag()

        while self.command_handler.get.cant_carry and not self.stopping:
            magentaprint("GrindThread.get_items, number of steel bottles: " + str(self.inventory.count('steel bottle')))
            if self.inventory.count('steel bottle') > 1:
                # TODO: make an Ability for steel bottle (protection spell)
                self.command_handler.use.by_name('steel bottle')
                self.command_handler.use.wait_for_flag()
            elif self.inventory.count_restoratives() > 6:
                # self.command_handler.potion_thread_handler.consume.healing_potion()
                # self.command_handler.potion_thread_handler.consume.wait_for_flag()
                self.command_handler.potion_thread_handler.consume.execute_and_wait()
                # if self.command_handler.use.error:
                if self.command_handler.potion_thread_handler.consume.error:
                    # What is this inventory bug
                    # What about drink error
                    # Ooookkkk we put in consume.error so we don't loop infinitely
                    # We also made sure that drink removes from inventory, also so we won't loop infinitely
                    # ACK small flasks don't always disappear

                    return
                # Could drop/consume smaller restoratives and keep scarlets - not very important though, those get dropped at tip later
            else:
                # just leave it there
                return
            self.command_handler.get.execute_and_wait('all')

    def engage_mobs_who_joined_in(self):
        # while self.character.MOBS_JOINED_IN != []:
        #     self.engage_monster(self.character.MOBS_JOINED_IN[0])
        #     self.character.MOBS_JOINED_IN = self.character.MOBS_JOINED_IN[1:]
        #     self.get_items()
        while self.character.mobs.attacking and not self.stopping:
            self.engage_monster(self.character.mobs.attacking[0])
            # self.character.mobs.attacking = self.character.mobs.attacking[1:]
            # self.get_items_if_weapon() # Could get loot blocked

    def engage_any_attacking_mobs(self):
        engaged = False

        # while self.character.MOBS_ATTACKING != []:
        while self.character.mobs.attacking != [] and not self.stopping:
            engaged = True
            self.engage_monster(self.character.mobs.attacking[0])

        # if engaged:
        #     self.get_items_if_weapon()

        return engaged

    def ready_for_combat(self):
        return self.character.HEALTH >= self.character.HEALTH_TO_HEAL and \
               self.character.MANA >= self.character.MANA_TO_ENGAGE and \
               hasattr(self.command_handler.weapon_bot, 'weapon') and \
               self.command_handler.weapon_bot.has_usable_weapon_in_inventory() 
               # TODO: Could be stricter about second weapon (this is is a lot of list checks)
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
