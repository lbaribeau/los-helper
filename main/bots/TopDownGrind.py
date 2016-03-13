
import time
import re
import threading
from threading import Thread
import atexit

from misc_functions import *
from Exceptions import *
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
from mini_bots.travel_bot import TravelBot

class TopDownGrind(Thread):
    def __init__(self, char, command_handler, mrh, db_handler):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        self.mrh = mrh
        self.db_handler = db_handler
        self.smartCombat = command_handler.smartCombat
        self.kill = command_handler.smartCombat.kill
        self.cast = command_handler.smartCombat.cast
        self.stopping = False

        self.actions = {
            # R.you_wield: (lambda self, match : self.weapon = match.group('weapon')),
            # R.off_hand: (lambda self, match : self.second = match.group('weapon')),
            R.you_wield[0]: self.react_to_wield,
            R.off_hand[0]: self.react_to_off_hand,
            R.weapon_break[0]: self.react_to_weapon_break,
            # R.weapon_break: lambda match : if
            R.weapon_shatters[0]: self.react_to_weapon_break
        }
        self.regex_cart = self.actions.keys()

    def notify(self, regex, match):
        self.actions[regex](match)

    def react_to_wield(self, match):
        self.weapon = match.group('weapon')

    def react_to_off_hand(self, match):
        self.second = match.group('second')

    def react_to_weapon_break(self, match):
        self.broken_weapon = match.group('weapon')

        if hasattr(self, 'weapon') and self.weapon == match.group('weapon'):
            del self.weapon  # self.weapon can be incorrectly deleted if th offhand is the same
        elif hasattr(self, 'second') and self.second == match.group('weapon'):
            del self.second

    def go_repair_or_replace_weapon(self):
        if not hasattr(self, 'weapon'):
            if hasattr(self, 'broken_weapon'):
                if self.try_weapons_from_inventory(self.broken_weapon):
                    del self.broken_weapon
                    return

                if self.inventory.has(self.broken_weapon):
                    self.go_to_nearest_smithy()

                    if self.repair_and_wield_broken_weapons(self.broken_weapon):
                        del self.broken_weapon
                        return

                self.go_buy_and_wield(self.broken_weapon)
                del self.broken_weapon
        else:
            raise Exception("TopDownGrind needs to choose a weapon from db.")

    def repair_and_wield_broken_weapons(self, w):
        weapon_ref = self.char.inventory.get_first_reference(w)
        while self.char.inventory.name_from_ref(weapon_ref) == w:
            self.command_handler.repair.execute_and_wait(weapon_ref)
            if self.command_handler.repair.success:
                self.rewield(weapon_ref)
                return True
            elif self.command_handler.repair.result == R.no_gold:
                raise Exception("No gold!")
            else:
                weapon_ref = MobTargetDeterminator().increment_ref(weapon_ref)

    def try_weapons_from_inventory(self, w):
        if self.inventory.has(w):
            if hasattr(self, 'weapon'):
                if self.try_reequipping_offhand(w):
                    self.second = w
                    return True
            else:
                self.command_handler.wield.execute_and_wait(self.char.inventory.get_reference(w, 2))

                if self.command_handler.wield.result in R.already_wielding:
                    if self.second:
                        self.weapon = self.second
                        del self.second
                        self.try_weapons_from_inventory(w)
                    else:
                        raise Exception("TopDownGrind.try_weapons confusion.")
                else:
                    if self.try_reequipping_mainhand(w):
                        self.weapon = w
                        return True

    def try_reequipping_mainhand(self, w):
        return self.try_rewielding(self.command_handler.wield, w)

    def try_reequipping_offhand(self, w):
        return self.try_rewielding(self.command_handler.wield.second, w)

    def try_rewielding(self, command_object, weapon_name):
        ref = self.char.inventory.get_reference(w, 2)

        command_object.execute_and_wait(ref)
        if command_object.success:
            return True

        while command_object.broken_error:
            self.inventory.set_broken(ref)
            ref = self.mob_target_determinator.increment_ref(ref)
            if self.char.inventory.get_item_name_from_reference(ref) == w:
                command_object.execute_and_wait(ref)
                if command_object.success:
                    return True
            else:
                return False

        # If offhand breaks, we need to try one wield and then correct our variables once we learn which broke of mainhand/offhand

    # def go_replace_weapon(self, w):
    #     self.go_buy_and_wield(self.shattered_weapon)
    #     del self.shattered_weapon

    #     bw = self.broken_weapon
    #     del self.broken_weapon
    #     self.go_buy_and_wield(bw)

    def rewield(self, weapon_ref):
        weapon_name = self.char.inventory.name_from_reference(weapon_ref)
        self.command_handler.wield.execute_and_wait(weapon_ref)
        if not self.command_handler.wield.success:
            self.command_handler.wield.second.execute_and_wait(weapon_ref)
            if not self.command_handler.wield.second.success:
                raise Exception("Couldn't rewield!")
            else:
                self.second = weapon_name
        else:
            self.weapon = weapon_name

    def stop(self):
        self.stopping = True

    def run(self):
        self.stopping = False

        while not self.stopping:
            if self.stopping:
                break

            self.go_repair_or_replace_weapon()
            self.go_repair_armour()
            self.go_sell_and_drop()

            if self.should_rest():
                self.go_rest()
            else:
                self.go_hunting()

    def go_to_nearest_smithy(self, grinding=False):
        magentaprint("TopDownGrind.go_to_nearest_smithy()")
        smithy_path = self.get_smithy_path()
        magentaprint("TopDownGrind.get_smithy_path(): " + str(smithy_path))
        travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.db_handler)
        travel_bot.follow_path(smithy_path)

    def get_smithy_path(self):
        try:
            paths = self.db_handler.get_smithy_paths(self.char.AREA_ID)
        except Exception as e:
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            magentaprint("Exception getting smithy path.")
            magentaprint(e, False)
            raise e

        if paths:
            return get_shortest_array(paths)
        else:
            magentaprint("SmartGrindThread.get_smithy_path() error... no exception but no path returned... make sure the DB is accessible.")
            self.rest_and_check_aura()
            return []

    def go_repair_armour(self):
        pass

    def go_sell_and_drop(self):
        pass

    # def should_rest(self):
    #     pass

    # Commented - algorithm change - we can do the same thing on shattered or broken
    # (try items in inventory, repair items in inventory, then go shopping)

    # def react_to_weapon_shatter(self, match):
    #     if hasattr(self, 'weapon') and hasattr(self, 'second') and self.weapon == self.second:
    #         # self.unknown_broken_weapon = True  # Unneeded because we will try both wield and second
    #         self.shattered_weapon = self.weapon
    #     elif hasattr(self, 'weapon') and self.weapon == match.group('weapon'):
    #         self.shattered_weapon = self.weapon
    #         del self.weapon
    #     elif hasattr(self, 'second') and self.second == match.group('weapon'):
    #         self.shattered_weapon = self.second
    #         del self.second
    #     else:
    #         magentaprint("TopDownGrind.react_to_weapon_shatter error case.")

    # def go_repair_or_replace_weapon(self):
    #     if hasattr(self, 'broken_weapon'):
    #         if self.try_weapons_from_inventory(self.broken_weapon):
    #             del self.broken_weapon
    #             return

    #         if self.inventory.has(self.broken_weapon):
    #             self.go_to_nearest_smithy()

    #             if self.repair_and_wield_broken_weapons(self.broken_weapon):
    #                 del self.broken_weapon
    #                 return

    #         self.go_buy_and_wield(self.broken_weapon)
    #         del self.broken_weapon

    #     elif hasattr(self, 'shattered_weapon'):
    #         if self.try_weapons_from_inventory(self.shattered_weapon):
    #             del self.shattered_weapon
    #             return

    #         if self.inventory.has(self.shattered_weapon):
    #             self.go_to_nearest_smithy()

    #             if self.repair_and_wield_broken_weapons(self.shattered_weapon):
    #                 del self.shattered_weapon
    #                 return

    #         self.go_buy_and_wield(self.shattered_weapon)
    #         del self.shattered_weapon
    #     # if hasattr(self, 'broken_weapon') or hasattr(self, 'shattered_weapon'):

