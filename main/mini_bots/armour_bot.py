
import time
import re

from misc_functions import *
from Exceptions import *
from comm                           import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
from mini_bots.travel_bot           import TravelBot
from mini_bots.smithy_bot           import SmithyBot
from mini_bots.shopping_bot         import ShoppingBot
from mini_bots.mini_bot             import MiniBot
from db.Database                    import AreaStoreItem

class ArmourBot(MiniBot):
    def __init__(self, char, command_handler, map):
        super().__init__()
        self.char = char
        self.inventory = self.char.inventory 
        self.command_handler = command_handler
        self.map = map
        self.broken_armour = []

        # self.actions = {
        #     R.armour_breaks[0]: self.react_to_armour_break,
        # }
        # self.regex_cart = self.actions.keys()
        self.regex_cart = [R.armour_breaks, R.repair]
        self.actions = {
            R.armour_breaks[0]: self.react_to_armour_break,
            R.repair[0]: self.react_to_repair
        }
        # magentaprint("ArmourBot regex cart: " + str(self.regex_cart))
        # self.thread = None  # smithy_bot or shopping_bot
        # self.stopping = False  # backwards compatibility
        self.stopping = False
        self.smithy_bot = SmithyBot(self.char, self.command_handler, self.map)
        self.shopping_bot = ShoppingBot(self.char, self.command_handler, self.map)
        self.travel_bot = TravelBot(self.char, self.command_handler, self.map)

    def stop(self):
    # use parent stop() on self.thread hitting a smithy_bot or a shopping_bot doesn't work because that thread refers to
    # a call on self.suit_up().  Processing may fall into SmithyBot, and for stop to work, stop() has to be written to be able
    # to access that scope.
        self.stopping = True
        self.smithy_bot.stop()
        self.shopping_bot.stop()
        self.travel_bot.stop()

    # def start_thread(self):
    #     self.suit_up()

    def run(self):
        # MiniBot uses this to start a thread.
        self.suit_up()

    def notify(self, regex, match):
        self.actions[regex](match)

    def react_to_armour_break(self, match):
        if len(match.group('item').split()) == 2 and match.group('item').split()[1] == 'ring':
            return
        else:
            self.broken_armour.append(match.group('item'))

    def react_to_repair(self, match):
        if match.group(1) in self.broken_armour:
            magentaprint("Armour bot removed " + match.group(1) + "from self.broken_armour.")
            self.broken_armour.remove(match.group(1))

    def suit_up(self):
        magentaprint("ArmourBot suit_up()")
        # Maybe start by checking self.broken_armour
        # We know the armour broke, but we can't assume it didn't get dropped
        # Unless we have the bot keep broken armour...
        self.go_repair_or_replace_broken_armour()
        self.get_needed_default_armour()
        # Need to cancel if inventory doesn't have the broken armour piece (user manually repairs armour)

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
        # These functions can unset self.broken_armour if they successfully wear a piece
        # And they operate on self.broken_armour

        # if self.do_for_each_broken_piece(self.try_armour_from_inventory):
        #     return

        self.do_for_each_broken_piece(self.try_armour_from_inventory)

        # if any(a in [i.name for i in self.inventory.list] for a in self.broken_armour):
        # if self.broken_armour:
        if any(a in [i.name for i in self.inventory.list] for a in self.broken_armour):
            self.go_to_nearest_smithy()

        self.do_for_each_broken_piece(self.repair_and_wear)
        self.do_for_each_broken_piece(self.go_buy_and_wear)  # I think we'll skip this bit and rely on the default armour
            # We should make all the paths beforehand to ensure an efficient shopping trip
        self.broken_armour = []  # If it couldn't be bought, it's time to forget about it.

        # self.broken_armour = self.try_armour_from_inventory(self.broken_armour[:])
        # self.go_to_nearest_smithy()
        # self.broken_armour = self.repair_and_wear_armour_from_inventory(self.broken_armour[:])
        # self.broken_armour = self.go_buy_and_wear_armour(self.broken_armour[:])

    def do_for_each_broken_piece(self, function):
        list_copy = self.broken_armour[:]

        for a in self.broken_armour:
            if a:
                if function(a):
                    list_copy.remove(a)

        self.broken_armour = list_copy

    def try_armour_from_inventory(self, a):
        ref = self.char.inventory.get_first_reference(a)

        if ref is None:
            # Armour breaks on the way to the tpi, the bot trashes it before armour bot gets called, we end up here
            return

        last_ref_plus_one = MobTargetDeterminator().increment_ref(self.char.inventory.get_last_reference(a))
        # Did this just assume that the last one is the broken one (fixed)
        # Why trust is_broken if we don't have to

        while ref != last_ref_plus_one:
            # Is it safe to do it this way... I think so... (or can it miss and loop infinitely)
            self.command_handler.wear.execute_and_wait(ref)
            if self.command_handler.wear.success:
                return True
            else:
                ref = MobTargetDeterminator().increment_ref(ref)

    def repair_and_wear(self, a):
        armour_ref = self.char.inventory.get_last_reference(a)
        magentaprint("ArmourBot.repair_and_wear on " + str(a) + ", armour_ref: " + str(armour_ref))
        if armour_ref:
            while self.char.inventory.name_from_reference(armour_ref) == a:
                self.command_handler.repair.execute_and_wait(armour_ref)
                if self.command_handler.repair.success:
                    # The smithy doesn't take and give back the item (same ref is good)
                    self.command_handler.wear.execute_and_wait(armour_ref)
                    if self.command_handler.wear.success:
                        return True
                    else:
                        # This can be when the smithy is angry - you can't do that because you're fighting...
                        # raise Exception("ArmourBot - wear should have worked there.")
                        magentaprint("UNCOMMON EXCEPTION - wear should have worked there.")
                        return False 
                        # Try returning... maybe the bot will reset, try going back to chapel, call suit up again and finish the job
                        # What if Hurn blocks us, maybe travel-bot will exit also
                        # Could be that something got put on in that slot (ie. after a 'wear all' for ring wearing)
                elif self.command_handler.repair.failure:
                    # self.char.inventory.remove_by_ref(armour_ref) # Repair does this
                    # armour_ref = MobTargetDeterminator().decrement_ref(armour_ref) 
                    # Do the next piece?? No decrement ref could get something else
                    # Ok the loop condition would have caught that - call get_last_reference here anyway
                    armour_ref = self.char.inventory.get_last_reference(a)
                    # Contiue loop (try next in inventory if there is one)
                elif self.command_handler.repair.result is R.cant_repair:
                    # This can happen if the character was wearing something odd, so don't raise an exception
                    # ie. big nose and glasses
                    # Caller will remove it from the broken list
                    return True
                else:
                    magentaprint("Confused ArmourBot.")
                    # Could try go to smithy again here if necessary
                    # "It's not broken yet".... well my command was wrong... steel 3 not steel 2...
                    # That was from assuming in try_armour_from_inventory that the last ref was going to be the broken one
                    raise
        else:
            magentaprint("ArmourBot.repair_and_wear() error - no inventory ref for " + str(a) + ".")  
            # Todo? What if the armour fell apart... then it's not in inventory...

    def go_buy_and_wear(self, a):
        # I think we won't try to shop for the same armour that just broke, and just fall back immediately to the default set
        pass

    def get_needed_default_armour(self):
        # Given size, armor level, slot, choose best piece from shop
        # Ie. steel, medium, neck - plate mail collar
        #desired_items = sorted(self.determine_shopping_list(self.broken_armour), key=lambda item : item.area)
        # We don't need to use broken armour here, since we've been to the smithy.  We should check equipment (I feel uncertain about the order of actions).

        # travel_bot = TravelBot(self.char, self.command_handler, self.map)
        # shopping_bot = ShoppingBot(self.char, self.command_handler, self.map)
        self.stopping = False
        desired_asi_list = self.determine_shopping_list(self.broken_armour)
        # magentaprint("ArmourBot.get_needed_default_armour() desired_asi_list: " + str(desired_asi_list))

        for asi in desired_asi_list:
            if self.stopping:
                return
            # path = self.map.get_path(self.char.AREA_ID, asi.area.id)
            # travel_bot.follow_path(path)
            self.travel_bot.go_to_area(asi.area.id)
            if self.stopping:
                return
            if self.shopping_bot.buy_from_shop(asi):
                self.command_handler.wear.execute_and_wait(self.char.inventory.get_last_reference(str(asi.item.name)))
                if self.command_handler.wear.result == R.no_room:
                    # This is probably the equipment command messing up and buying unnecessarily
                    # The equipment dict didn't get set up right
                    self.get_needed_default_armour() 
                    # This will call determine_shopping_list again
                    break # This will prevent finishing the current version of the loop
                if asi.item.name in self.broken_armour:
                    self.broken_armour.remove(asi.item.name)
                else:
                    self.broken_armour = []
            else:
                # TODO: a) check character max weight agains item weight and only travel and buy if the item can be carried
                # or b) go on a vendor/recycling trip and come back
                pass

    # def go_to_nearest_smithy(self, grinding=False):
    #     magentaprint("TopDownGrind.go_to_nearest_smithy()")
    #     smithy_path = self.get_smithy_path()
    #     magentaprint("TopDownGrind.get_smithy_path(): " + str(smithy_path))
    #     self.travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.map)
    #     self.travel_bot.follow_path(smithy_path)

    def determine_shopping_list(self, broken_armour):
        # items = []
        # for a in broken_armour:
        #     # wear_location = map.lookup_wear_location(a)A
        #     db_item = Item.get_item_by_name(a)
        #     if db_item and db_item.itemtype and db_item.itemtype.data:
        #         wear_location = db_item.itemtype.data
        #         desired_item = self.pick_areastoreitem(wear_location, self.char.class_string, self.char.info.race, self.char.info.level)
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
                # size = self.determine_size(self.char.info.race)
                # level = self.determine_armour_level(self.char.class_string)
                # size = ArmourSizeDeterminator().determine(self.char.info.race)
                # level = ArmourLevelDeterminator().determine(self.char.class_string)
                size = self.get_size(self.char.info.race)
                level = self.get_armour_level(self.char.info.level)  # checks class and level (low level paladin can't wear steel yet)
                # magentaprint("armour_bot.determine_shopping_list() size: " + size + ", slot: " + str(slot) + ", level: " + str(level))
                if slot == 'wielded' or slot == 'seconded':
                    continue
                if slot == 'face' or slot == 'holding':
                    continue  # no masks in shops, so this hack will probably stay.  We should add 'face' slot to the db.
                if re.search(r'\d$', slot):
                    slot = slot[:len(slot)-1]  # neck2, finger3, etc.
                slot = slot.title()
                # items = AreaStoreItem.get_by_item_type_and_level_max(size, slot, level)
                items = AreaStoreItem.get_buyable_armour(size, slot, level)
                #magentaprint("determine_shopping_list() items: " + str(items))
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
                #dir(items)
                # magentaprint("ArmourBot determine_shopping_list() size {0}, slot {1}, level {2}, found {3}".format(size, slot, level, str(items)))
                for item in items:
                    # magentaprint("Won't print if there's no valid item: " + str(item))
                    # Don't bother sorting for now
                    desired_items.append(item)
                    break

        #magentaprint("Armour bot shopping list " + str(desired_items))
        # magentaprint("Armour bot shopping list: \n" + str([asi.item.name for asi in desired_items]))
        magentaprint("ARMOUR BOT SHOPPING LIST: \n" + "\n".join("    {} {}".format(asi.item, asi.item.name) for asi in desired_items))
        magentaprint("Size: {}; Level: {}".format(self.get_size(self.char.info.race), self.get_armour_level(self.char.info.level)))
        return desired_items
        # TODO: One issue: shields aren't sized - so queries that use any size need to return the shield, whose type may be
        # the generic armour type.   SELECT "t1"."id", "t1"."area_id", "t1"."item_id" FROM "areastoreitem" AS t1 INNER JOIN "item"
        # AS t2 ON ("t1"."item_id" = "t2"."id") INNER JOIN "itemtype"
        # AS t3 ON ("t2"."itemtype_id" = "t3"."id") WHERE (("t2"."level" <= ?) AND (("t3"."model_id" = ?) AND ("t3"."data_id" = ?)))

        # for slot in ['body','arms','legs','neck1','neck2','face','hands','head', 'shield']:

    def pick_areastoreitem(self, slot, cls, race, character_lvl):
        # We will use the class to determine the armour level, we have the slot as a string so we'll select data with that,
        # and we need to map that character level to the allowed armour tiers.
        if cls == 'Mon':
            return

        items = AreaStoreItem.get_by_item_type_and_level_max(
            self.get_size(race), 
            slot, 
            self.get_armour_level(character_lvl)
        )

        if items:
            items.sort(key=lambda item: item.level, reverse=True)
            return items[0]

    def get_armour_level(self, character_lvl):
        # cloth, ring mail, chain, plate, steel (1-5)
        if self.steel():
            if character_lvl > 9:
                return 5
            else:
                return 4
        elif self.chain():
            if character_lvl > 9:
                return 3
            else:
                return 2
        else:
            return 1

    def get_size(self, race):
        if race.lower() in ['hobbit','halfling','half-elf','gnome','dark-elf','dwarf']:
            return 's-armor'
        elif race.lower() in ['human','half-orc','elf']:
            return 'm-armor'
        elif race.lower() in ['half-giant']:
            return 'l-armor'
        else:
            # raise Exception("ArmourBot doesn't know what size of armour to get.")
            magentaprint("WARNING: ArmourBot doesn't know what size of armour to get")
            return None

    def no_armour(self):
        return self.char.class_string == 'Mon'
    def clothie(self):
        return self.char.class_string in ["Mag"]
    # def leather(self):
    #     return self.char.class_string in ['Dru', 'Alc', 'Thi']
    def chain(self):
        return self.char.class_string in ['Alc', 'Thi', 'Dru', 'Ran', 'Cle', 'Ass']
    def steel(self):
        #magentaprint("ArmourBot.steel() class string is: " + str(self.char.class_string))
        return self.char.class_string in ['Pal', 'Dk', 'Bar', 'Fig', 'Brd']

    def go_to_nearest_smithy(self):
        # self.thread.stop()
        # self.thread = SmithyBot(self.char, self.command_handler, self.mrh, self.map)
        # self.thread.start_thread()
        # s = SmithyBot(self.char, self.command_handler, self.mrh, self.map)
        # s.go_to_nearest_smithy()
        self.smithy_bot.go_to_nearest_smithy()

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


