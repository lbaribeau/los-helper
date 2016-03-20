
import time
import re

from misc_functions import *
from Exceptions import *
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
from mini_bots.travel_bot import TravelBot
from mini_bots.equipment_bot import EquipmentBot

class ArmourBot(EquipmentBot):
    def __init__(self, char, command_handler, mrh, db_handler):
        super().__init__(char, command_handler, mrh, db_handler)
        self.broken_armour = []

        # self.actions = {
        #     R.armour_breaks[0]: self.react_to_armour_break,
        # }
        # self.regex_cart = self.actions.keys()
        self.actions = {R.armour_breaks[0]: self.react_to_armour_break}
        self.regex_cart = [R.armour_breaks]
        # magentaprint("ArmourBot regex cart: " + str(self.regex_cart))

    def notify(self, regex, match):
        self.actions[regex](match)

    def react_to_armour_break(self, match):
        self.broken_armour.append(match.group('item'))

    def suit_up(self):
        magentaprint("ArmourBot suit_up()")
        self.go_repair_or_replace_broken_armour()
        self.get_needed_default_armour()

    # def go_repair_or_replace_broken_armour(self):
    #     broken_armour_copy = self.broken_armour[:]

    #     for piece in self.broken_armour:
    #         if self.try_armour_from_inventory(piece):
    #             broken_armour_copy.remove(piece)
    #             continue

    #         self.go_to_nearest_smithy()

    #         if self.repair_and_wear(piece):
    #             broken_armour_copy.remove(piece)
    #             continue

    #         if self.go_buy_and_wear(piece):
    #             broken_armour_copy.remove(piece)
    #             continue

    #     self.broken_armour = broken_armour_copy
    def go_repair_or_replace_broken_armour(self):
        self.do_for_each_piece(self.try_armour_from_inventory)

        if self.broken_armour:
            self.go_to_nearest_smithy()

        self.do_for_each_piece(self.repair_and_wear)
        self.do_for_each_piece(self.go_buy_and_wear)
            # We should make all the paths beforehand to ensure an efficient shopping trip

        # self.broken_armour = self.try_armour_from_inventory(self.broken_armour[:])
        # self.go_to_nearest_smithy()
        # self.broken_armour = self.repair_and_wear_armour_from_inventory(self.broken_armour[:])
        # self.broken_armour = self.go_buy_and_wear_armour(self.broken_armour[:])

    def do_for_each_piece(self, function):
        list_copy = self.broken_armour[:]

        for a in self.broken_armour:
            if function(a):
                list_copy.remove(a)

        self.broken_armour = list_copy

    def try_armour_from_inventory(self, a):
        ref = self.char.inventory.get_first_reference(a)
        last_ref = self.char.inventory.get_last_reference(a)

        while ref != last_ref:
            self.command_handler.wear.execute_and_wait(ref)
            if self.command_handler.wear.success:
                return True
            else:
                ref = MobTargetDeterminator().increment_ref(ref)

    def repair_and_wear(self, a):
        armour_ref = self.char.inventory.get_last_reference(a)
        while self.char.inventory.name_from_reference(armour_ref) == a:
            self.command_handler.repair.execute_and_wait(armour_ref)
            if self.command_handler.repair.success:
                self.command_handler.wear.execute_and_wait(armour_ref)
                if self.command_handler.wear.success:
                    return True
                else:
                    raise Exception("ArmourBot - not sure why that didn't work.")
            else:
                self.char.inventory.remove_by_ref(armour_ref)
                armour_ref = MobTargetDeterminator().decrement_ref(armour_ref)

    def go_buy_and_wear(self, a):
        pass

    def get_needed_default_armour(self):
        pass
