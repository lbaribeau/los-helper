
import time
import re

from misc_functions import *
from Exceptions import *
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
from mini_bots.travel_bot import TravelBot
from mini_bots.smithy_bot import SmithyBot
from mini_bots.shopping_bot import ShoppingBot

class ArmourBot(SmithyBot):
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
        # Given size, armor level, slot, choose best piece from shop
        # Ie. steel, medium, neck - plate mail collar
        #desired_items = sorted(self.determine_shopping_list(self.broken_armour), key=lambda item : item.area)
        # We don't need to use broken armour here, since we've been to the smithy.  We should check equipment (I feel uncertain about the order of actions).

        self.travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.map)
        shopping_bot = ShoppingBot(self.char, self.command_handler)
        desired_asi_list = self.determine_shopping_list(self.broken_armour)
        # magentaprint("ArmourBot.get_needed_default_armour() desired_asi_list: " + str(desired_asi_list))

        for asi in desired_asi_list:
            path = self.map.get_path(self.char.AREA_ID, asi.area.id)
            self.travel_bot.follow_path(path)
            if shopping_bot.buy_from_shop(asi):
                self.command_handler.wear.execute_and_wait(self.char.inventory.get_last_reference(str(asi.item.name)))
            else:
                # TODO: a) check character max weight agains item weight and only travel and buy if the item can be carried
                # or b) go on a vendor/recycling trip and come back
                pass

    def go_to_nearest_smithy(self, grinding=False):
        magentaprint("TopDownGrind.go_to_nearest_smithy()")
        smithy_path = self.get_smithy_path()
        magentaprint("TopDownGrind.get_smithy_path(): " + str(smithy_path))
        self.travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.map)
        self.travel_bot.follow_path(smithy_path)

    def determine_shopping_list(self, broken_armour):
        # items = []
        # for a in broken_armour:
        #     # wear_location = map.lookup_wear_location(a)A
        #     db_item = Item.get_item_by_name(a)
        #     if db_item and db_item.itemtype and db_item.itemtype.data:
        #         wear_location = db_item.itemtype.data
        #         desired_item = self.pick_areastoreitem(wear_location, self.char.class_string, self.char.race, self.char.level)
        #         if desired_item and desired_item.area:
        #             items.append(desired_item)
        #         else:
        #             magentaprint("ArmourBot couldn't pick out a default armour piece for " + wear_location.lower() + " slot.")

        # return items
        # Should we prefer the item that was just broken?  No need, that's overcomplicating it.  Go to the DB.

        # Steel armour: Paladins, dark knights, barbarians, fighters, bards(?) (cast iron shield)
        # Plate same as Steel maybe (large iron shield)
        # Chain: Rangers, assassins, clerics (iron shield)
        # Ring mail: Mages, druids, alchemists, thieves (bone shield)

        self.command_handler.equipment.execute_and_wait()
        desired_items = []

        for slot in self.command_handler.equipment.slot_names:
            if self.command_handler.equipment.dict[slot]:
                continue
            else:
                # Search db for a piece given size, class, slot
                # size = self.determine_size(self.char.race)
                # level = self.determine_armour_level(self.char.class_string)
                # size = ArmourSizeDeterminator().determine(self.char.race)
                # level = ArmourLevelDeterminator().determine(self.char.class_string)
                size = self.get_size(self.char.race)
                level = self.get_armour_level(self.char.level)  # checks class and level (low level paladin can't wear steel yet)
                magentaprint("determine_shopping_list() size " + size + ", slot: " + str(slot) + ", level: " + str(level))
                if slot == 'wielded' or slot == 'seconded':
                    continue
                if slot == 'face' or slot == 'holding':
                    continue  # no masks in shops, so this hack will probably stay.  We should add 'face' slot to the db.
                if re.search(r'\d$', slot):
                    slot = slot[:len(slot)-1]  # neck2, finger3, etc.
                slot = slot.title()
                items = AreaStoreItem.get_by_item_type_and_level_max(size, slot, level)
                magentaprint("determine_shopping_list() items: " + str(items))
                # if items:
                #     if len(items) > 0:
                #         magentaprint(str(len(items)))  # Object of type 'SelectQuery' has no len()
                #         magentaprint("determine_shopping_list() items[0]: " + str(items[0]))
                #         magentaprint("determine_shopping_list() items[0].level: " + str(items[0].level))
                #         items.sort(key=lambda item: item.level, reverse=True)
                #         desired_items.append(items[0])
                # if items:
                #     items.sort(key=lambda item: item.level, reverse=True)  # Use the highest level match
                #     # 'SelectQuery' object has no attribute 'sort'  ... maybe it is an iterator though
                #     magentaprint("determine_shopping_list chose " + items[0].item.name)
                #     desired_items.append(items[0])
                dir(items)
                for item in items:
                    magentaprint("Won't print if there's no valid item: " + str(item))
                    # Don't bother sorting for now
                    desired_items.append(item)
                    break

        return desired_items

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
        elif character_lvl > 4:
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
        magentaprint("ArmourBot.steel() class string is: " + str(self.char.class_string))
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


