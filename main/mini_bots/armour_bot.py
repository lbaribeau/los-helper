
import time
import re

from misc_functions import *
from Exceptions import *
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
from mini_bots.travel_bot import TravelBot
from mini_bots.equipment_bot import EquipmentBot
from mini_bots.shopping_bot import ShoppingBot

class ArmourBot(EquipmentBot):
    def __init__(self, char, command_handler, mrh, map):
        super().__init__(char, command_handler, mrh, map)
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
        if len(match.group('item').split()) == 2 and match.group('item').split()[1] == 'ring':
            return
        else:
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
        self.do_for_each_piece(self.go_buy_and_wear)  # I think we'll skip this bit and rely on the default armour
            # We should make all the paths beforehand to ensure an efficient shopping trip

        # self.broken_armour = self.try_armour_from_inventory(self.broken_armour[:])
        # self.go_to_nearest_smithy()
        # self.broken_armour = self.repair_and_wear_armour_from_inventory(self.broken_armour[:])
        # self.broken_armour = self.go_buy_and_wear_armour(self.broken_armour[:])

    def do_for_each_piece(self, function):
        list_copy = self.broken_armour[:]

        for a in self.broken_armour:
            if a:
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
        magentaprint("ArmourBot.repair_and_wear on " + str(a) + ", armour_ref: " + str(armour_ref))
        while self.char.inventory.name_from_reference(armour_ref) == a:
            self.command_handler.repair.execute_and_wait(armour_ref)
            if self.command_handler.repair.success:
                self.command_handler.wear.execute_and_wait(armour_ref)
                if self.command_handler.wear.success:
                    return True
                else:
                    raise Exception("ArmourBot - not sure why that didn't work.")
                    # Could be that something got put on in that slot (ie. after a 'wear all' for ring wearing)
            else:
                self.char.inventory.remove_by_ref(armour_ref)
                armour_ref = MobTargetDeterminator().decrement_ref(armour_ref)

    def go_buy_and_wear(self, a):
        # I think we won't try to shop for the same armour that just broke, and just fall back immediately to the default set
        pass

    def get_needed_default_armour(self):
        # Steel armour: Paladins, dark knights, barbarians, fighters, bards(?) (cast iron shield)
        # Plate same as Steel maybe (large iron shield)
        # Chain: Rangers, assassins, clerics (iron shield)
        # Leather: druids, Alchemists, thieves (bone shield)
        # Ring mail: mages
        # Clothies: ring mail and bone shield

        # Given size, armor level, slot, choose best piece from shop
        # Ie. steel, medium, neck - plate mail collar
        desired_items = sorted(self.determine_shopping_list(self.broken_armour), key=lambda item : item.area)
        travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.map)
        shopping_bot = ShoppingBot(self.char, self.command_handler)
        magentaprint("ArmourBot.get_needed_default_armour() desired_items: " + str(desired_items))

        for item in desired_items:
            path = self.map.get_path(self.char.AREA_ID, item.area)
            travel_bot.follow_path(path)
            shopping_bot.buy_from_shop(item)
            self.command_handler.wear.execute_and_wait(self.char.inventory.get_last_reference(str(item)))

    def go_to_nearest_smithy(self, grinding=False):
        magentaprint("TopDownGrind.go_to_nearest_smithy()")
        smithy_path = self.get_smithy_path()
        magentaprint("TopDownGrind.get_smithy_path(): " + str(smithy_path))
        self.travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.map)
        self.travel_bot.follow_path(smithy_path)

    def determine_shopping_list(self, broken_armour):
        items = []
        for a in broken_armour:
            # wear_location = map.lookup_wear_location(a)A
            db_item = Item.get_item_by_name(a)
            if db_item and db_item.itemtype and db_item.itemtype.data:
                wear_location = db_item.itemtype.data
                desired_item = self.pick_areastoreitem(wear_location, self.char.class_string, self.char.race, self.char.level)
                if desired_item and desired_item.area:
                    items.append(desired_item)
                else:
                    magentaprint("ArmourBot couldn't pick out a default armour piece for " + wear_location.lower() + " slot.")

        return items

        # for slot in ['body','arms','legs','neck1','neck2','face','hands','head', 'shield']:

    def pick_areastoreitem(self, slot, cls, race, character_lvl):
        # We will use the class to determine the armour level, we have the slot as a string so we'll select data with that,
        # and we need to map that character level to the allowed armour tiers.
        if cls == 'Mon':
            return

        armour_level = self.get_armour_level(character_lvl)
        size = self.get_size(race)

        # Select an armour comparing data to slot with the given armour level
        items = AreaStoreItem.get_by_item_type_and_level_max(size, slot, armour_level)

        if items:
            items.sort(key=lambda item: item.level, reverse=True)
            return items[0]

    def get_armour_level(self, character_lvl):
        if character_lvl > 9:
            if self.steel():
                return 3
            elif self.chain():
                return 2
            else:
                return 1
        elif character_level > 4:
            if self.clothie():
                return 1
            else:
                return 2
        else:
            return 1

    def get_size(self, race):
        if race.lower() in ['hobbit','halfling','half-elf','gnome','dark-elf','dwarf']:
            return 's-armor'
        elif race.lower() in ['human', 'half-orc','elf']:
            return 'm-armor'
        elif race.lower() in ['half-giant']:
            return 'l-armor'
        else:
            # raise Exception("ArmourBot doesn't know what size of armour to get.")
            return None

    def no_armour(self):
        return self.char.class_string == 'Mon'

    def clothie(self):
        return self.char.class_string in ["Mag", 'Dru', 'Alc', 'Thi']

    # def leather(self):
    #     return self.char.class_string in ['Dru', 'Alc', 'Thi']

    def chain(self):
        return self.char.class_string in ['Ran', 'Cle', 'Ass']

    def steel(self):
        return self.char.class_string in ['Pal', 'Dk', 'Bar', 'Fig', 'Brd']


    # # Use db for this?  Makes sense to
    # def is_body(self, string):
    #     pass

    # def is_arms(self, string):
    #     pass

    # def is_legs(self, string):
    #     pass

    # def is_neck(self, string):
    #     pass

    # def is_face(self, string):
    #     pass

    # def is_hands(self, string):
    #     pass

    # def is_head(self, string):
    #     pass


