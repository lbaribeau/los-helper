
import time
import re

from misc_functions import *
from Exceptions import *
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
# from mini_bots.travel_bot import TravelBot
from mini_bots.smithy_bot import SmithyBot
from mini_bots.mini_bot import MiniBot
from mini_bots.shopping_bot import ShoppingBot

class WeaponBot(MiniBot):
    def __init__(self, char, command_handler, mrh, mud_map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler

        self.actions = {
            # R.you_wield: (lambda self, match : self.weapon = match.group('weapon')),
            # R.off_hand: (lambda self, match : self.second = match.group('weapon')),
            R.you_wield[0]: self.react_to_wield,
            R.off_hand[0]: self.react_to_off_hand,
            R.weapon_break[0]: self.react_to_weapon_break,
            # R.weapon_break: lambda match : if
            R.weapon_shatters[0]: self.react_to_weapon_break,
            R.shield[0]: self.set_shield_or_offhand
        }
        # self.regex_cart = self.actions.keys()
        self.regex_cart = [R.you_wield, R.off_hand, R.weapon_break, R.weapon_shatters, R.shield]
        self.smithy_bot = None
        self.broken_weapon = []
        self.possible_weapons = []
        self.smithy_bot = SmithyBot(self.char, self.command_handler, mrh, mud_map)
        self.shopping_bot = ShoppingBot(char, command_handler, mrh, mud_map)
        self.shield_or_offhand = False

    def notify(self, regex, match):
        self.actions[regex](match)

    def react_to_wield(self, match):
        self.weapon = match.group('weapon')

    def react_to_off_hand(self, match):
        self.sheild_or_offhand = True
        self.second = match.group('second')

    def react_to_weapon_break(self, match):
        self.broken_weapon.append(match.group('weapon'))

        if hasattr(self, 'weapon') and self.weapon == match.group('weapon'):
            del self.weapon  # self.weapon can be incorrectly deleted if th offhand is the same
        elif hasattr(self, 'second') and self.second == match.group('weapon'):
            self.shield_or_offhand = False
            del self.second

    def set_shield_or_offhand(self, match=None):
        self.shield_or_offhand = True

    def run(self):
        self.check_weapons()

    def check_weapons(self):
        if hasattr(self, 'weapon') and self.shield_or_offhand:  # ArmourBot or eq should be called first...
            return
        else:
            self.repair_or_replace_weapon()

    def repair_or_replace_weapon(self):
        # if hasattr(self, 'broken_weapon'):
        broken_weapon_copy = self.broken_weapon[:]

        for w in broken_weapon_copy:
            if self.try_weapon_from_inventory(w):
                self.broken_weapon.remove(w)

        broken_weapon_copy = self.broken_weapon[:]

        for w in broken_weapon_copy:
            while self.char.inventory.has(w):
                if self.stopping:
                    return

                self.smithy_bot.go_to_nearest_smithy()

                if self.repair(w):
                    self.rewield(self.char.inventory.get_last_reference(w))
                    self.broken_weapon.remove(w)

        # broken_weapon_copy = self.broken_weapon[:]
        if self.broken_weapon:
            self.broken_weapon = []
        else:
            return

        if self.try_other_possible_weapons_in_inventory():
            return

        self.go_buy_replacement()

    def try_other_possible_weapons_in_inventory(self):
        magentaprint("WeaponBot.try_other_possible_weapons_in_inventory() " + str(self.get_possible_weapons()))
        for w in self.get_possible_weapons():
            if self.try_weapon_from_inventory(w.item.name):
                return True

        for w in self.get_possible_weapons():
            while self.char.inventory.has(w.item.name):
                if self.stopping:
                    return False

                self.smithy_bot.go_to_nearest_smithy()

                if self.repair(w.item.name):
                    self.rewield(self.char.inventory.get_last_reference(w.item.name))
                    return True

    def go_buy_replacement(self):
        if self.stopping:
            return
        # self.possible_weapons[0].map()
        magentaprint("WeaponBot.go_buy_replacement() calling shopping_bot.go_buy " + str(self.possible_weapons[0]))
        magentaprint("WeaponBot.go_buy_replacement() possible_weapons: " + str(self.possible_weapons))
        if self.shopping_bot.go_buy(self.possible_weapons[0]):
            self.rewield(self.char.inventory.get_last_reference(self.possible_weapons[0].item.name))

        # if self.go_purchase_item(possible_weapons[0]):
        # magentaprint("GrindThread.go_purchase_item() got location id: " + str(item.get_purchase_location_id()))
        # if item.get_purchase_location_id():
        #     self.direction_list = ["areaid%s" % item.get_purchase_location_id(), "dobuy%s" % item.to_string(), "areaid2"]
        #     return True
        # else:
        #     return False

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

    def stop(self):
        self.stopping = True
        self.smithy_bot.stop()
        self.shopping_bot.stop()

    # def go_repair(self):
    #     if hasattr(self, 'broken_weapon'):
    #         if self.try_weapons_from_inventory(self.broken_weapon):
    #             del self.broken_weapon
    #             return

    #         if self.char.inventory.has(self.broken_weapon):
    #             self.go_to_nearest_smithy()

    #             if self.repair_and_wield_broken_weapons(self.broken_weapon):
    #                 del self.broken_weapon
    #                 return

    #         # self.go_buy_and_wield(self.broken_weapon)  # Nevermind trying to buy the same, just go to the DB
    #         # del self.broken_weapon
    #     else:
    #         if not hasattr(self, 'weapon'):
    #             raise Exception("TopDownGrind needs to choose a weapon from db.")

    def repair(self, w):
        # weapon_ref = self.char.inventory.get_first_reference(w)
        weapon_ref = self.char.inventory.get_last_reference(w)
        # while self.char.inventory.name_from_ref(weapon_ref) == w:

        self.command_handler.repair.execute_and_wait(weapon_ref)
        if self.command_handler.repair.success:
            return True
        else:
            self.char.inventory.remove_by_ref(weapon_ref)
            return False

            # if self.command_handler.repair.success:
            #     self.rewield(weapon_ref)
            #     return True
            # elif self.command_handler.repair.result == R.no_gold:
            #     raise Exception("No gold!")
            # else:
            #     weapon_ref = MobTargetDeterminator().increment_ref(weapon_ref)

    def try_weapons_from_inventory(self, w):
        for w in self.broken_weapon:
            if self.try_weapon_from_inventory(w):
                self.broken_weapon.pop()

    def try_weapon_from_inventory(self, w):
        if self.char.inventory.has(w):
            if hasattr(self, 'weapon'):  # We know that the offhand broke
                if self.try_reequipping_offhand(w):
                    self.second = w
                    return True
            else:
                self.command_handler.smartCombat.wield.execute_and_wait(self.char.inventory.get_reference(w, 2))

                if self.command_handler.smartCombat.wield.result in R.already_wielding:
                    if self.second:
                        self.weapon = self.second
                        del self.second
                        self.shield_or_offhand = False
                        self.try_weapon_from_inventory(w)
                    else:
                        raise Exception("TopDownGrind.try_weapons confusion.")
                elif self.command_handler.smartCombat.wield.result in R.weapon_broken:
                    self.char.inventory.set_unusable(self.char.inventory.get_reference(w, 2))
                elif self.command_handler.smartCombat.wield.success:
                    return True
                else:
                    pass
                    # magentaprint("WeaponBot.try_weapon_from_inventory() tried " + str(w))
                    # if self.try_reequipping_mainhand(w):
                    #     self.weapon = w
                    #     return True

    def try_reequipping_mainhand(self, w):
        return self.try_rewielding(self.command_handler.smartCombat.wield, w)

    def try_reequipping_offhand(self, w):
        return self.try_rewielding(self.command_handler.smartCombat.wield.second, w)

    def try_rewielding(self, command_object, w):
        ref = self.char.inventory.get_reference(w, 2)

        command_object.execute_and_wait(ref)
        if command_object.success:
            return True

        while command_object.broken_error:
            self.char.inventory.set_broken(ref)
            ref = MobTargetDeterminator().increment_ref(ref)
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
        self.command_handler.smartCombat.wield.execute_and_wait(weapon_ref)
        if not self.command_handler.smartCombat.wield.success:
            self.command_handler.smartCombat.wield.second.execute_and_wait(weapon_ref)
            if not self.command_handler.smartCombat.wield.second.success:
                raise Exception("Couldn't rewield!")
            else:
                self.second = weapon_name
        else:
            self.weapon = weapon_name

    def go_to_nearest_smithy(self, grinding=False):
        # magentaprint("TopDownGrind.go_to_nearest_smithy()")
        # smithy_path = self.get_smithy_path()
        # magentaprint("TopDownGrind.get_smithy_path(): " + str(smithy_path))
        # self.travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.db_handler)
        # self.travel_bot.follow_path(smithy_path)
        # self.smithy_bot = SmithyBot(self.char, self.command_handler, self.mrh)
        self.smithy_bot.go_to_nearest_smithy()

    def get_possible_weapons(self):
        if self.possible_weapons:
            return self.possible_weapons
        else:
            self.possible_weapons = AreaStoreItem.get_by_item_type_and_level_max('weapon', self.char.weapon_type, self.char.weapon_level)
            self.possible_weapons = sorted(self.possible_weapons, key = lambda i: i.item.level, reverse=True)
            return self.possible_weapons

            # level = self.character.weapon_level
            # while not self.possible_weapons and level > 0:

            #     areastoreitems = AreaStoreItem.get_by_item_type_and_level(model_name, data_name, level)
            #     self.possible_weapons = list(MudItem.get_suitable_item_of_type('weapon', self.character.weapon_type, level).values())
            #     areastoreitems = AreaStoreItem.get_by_item_type_and_level(model_name, data_name, level)

            # while not self.possible_weapons and level > 0:
            #     magentaprint("check_weapons() trying lower level weapons.")
            #     self.possible_weapons = list(MudItem.get_suitable_item_of_type('weapon', self.character.weapon_type, level).values())
            #     level = level - 1

            # if not self.possible_weapons:
            #     magentaprint("WeaponBot didn't come up with a default weapon!")

            # return self.possible_weapons

    # def get_smithy_path(self):
    #     try:
    #         paths = self.db_handler.get_smithy_paths(self.char.AREA_ID)
    #     except Exception as e:
    #         #not a good situation - we can't find a way to the chapel from wherever we are
    #         #therefore we should just sit and wait here until we can go on the warpath again
    #         magentaprint("Exception getting smithy path.")
    #         magentaprint(e, False)
    #         raise e

    #     if paths:
    #         return get_shortest_array(paths)
    #     else:
    #         magentaprint("SmartGrindThread.get_smithy_path() error... no exception but no path returned... make sure the DB is accessible.")
    #         self.rest_and_check_aura()
    #         return []

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

    #         if self.char.inventory.has(self.broken_weapon):
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

    #         if self.char.inventory.has(self.shattered_weapon):
    #             self.go_to_nearest_smithy()

    #             if self.repair_and_wield_broken_weapons(self.shattered_weapon):
    #                 del self.shattered_weapon
    #                 return

    #         self.go_buy_and_wield(self.shattered_weapon)
    #         del self.shattered_weapon
    #     # if hasattr(self, 'broken_weapon') or hasattr(self, 'shattered_weapon'):

