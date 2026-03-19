
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
from db.Item                        import Item         
from math                           import ceil
from reactions.referencing_list     import ReferencingList

class ArmourBot(MiniBot):
    def __init__(self, char, command_handler, the_mud_map):
        super().__init__()
        self.char            = char
        self.inventory       = self.char.inventory 
        self.command_handler = command_handler
        self.map             = the_mud_map
        self.broken_armour   = []

        # self.actions = {
        #     R.armour_breaks[0]: self.react_to_armour_break,
        # }
        # self.regex_cart = self.actions.keys()
        self.regex_cart = [R.armour_breaks, R.repair]
        self.actions = {
            R.armour_breaks[0] : self.react_to_armour_break,
            R.repair[0]        : self.react_to_repair
        }
        # magentaprint("ArmourBot regex cart: " + str(self.regex_cart))
        # self.thread = None  # smithy_bot or shopping_bot
        # self.stopping = False  # backwards compatibility
        self.stopping     = False
        self.smithy_bot   = SmithyBot(self.char, self.command_handler, self.map)
        self.shopping_bot = ShoppingBot(self.char, self.command_handler, self.map)
        self.travel_bot   = TravelBot(self.char, self.command_handler, self.map)
        self.broken_list  = [] 

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
        # if len(match.group('item').split()) == 2 and match.group('item').split()[1] == 'ring':
        #     magentaprint("Armour bot skipping ring break")
        #     return
        # else:
        #     magentaprint("Armour bot got broken_armour: {}".format(match.group('item')))
        #     self.broken_armour.append(match.group('item'))
        self.broken_armour.append(match.group('item'))

    def react_to_repair(self, match):
        magentaprint("Armour bot repair reaction... no longer doing it this way")
        # if match.group(1) in self.broken_armour:
        #     magentaprint("Armour bot removed " + match.group(1) + "from self.broken_armour.")
        #     self.broken_armour.remove(match.group(1))

    def suit_up(self):
        magentaprint("ArmourBot suit_up()")
        # Maybe start by checking self.broken_armour
        # We know the armour broke, but we can't assume it didn't get dropped
        # Unless we have the bot keep broken armour...

        # if self.char.GOLD >= 3*self.command_handler.weapon_bot.possible_weapons[-1].item.value:
        #     # This check is up here indirectly because we aren't doing a lookup of the broken armour piece for cost
        #     # And saves going to the smithy when we can't afford it
        #     # The check was the wrong way... 
        #     # - Changed to last possible weapon beacuse 1st possible weapon is too strict when we hit 40% weapon skill...
        #     # - actually weapon code can use any of the weapons in its list now... has a few gold checks... armour bot can still refer to the cheapest weapon though
        #     # Ok but we don't want to skip repairing and then go buy it... could we link that logic
        #     # Can we make the repair code not kibosh weapon... but still run... supposing there is an ASI (area-store-item) for it
        #     self.go_repair_or_replace_broken_armour()

        self.stopping = False
        self.no_gold = False

        self.action_existing_broken_list() # Existing broken list is stuff we know from seeing regex come in, "Your _x_ fell apart" 
        # if self.no_gold or self.stopping:
        # Ehrm we still want the code to run to make .broken_list so we don't throw it all away
        if self.stopping:
            # The point here is, there could be items that we were wearing that we want to wear that don't come up from the DB query
            # It gets untenable if we start using the DB to clobber that... so we just give up if we didn't have that gold... we'll save it up
            magentaprint("Armour bot found no gold for regex broken list(?) stopping true anyway")
            return
        # Ok so what if we wear something other than broken_armour... couldn't afford it
        self.try_what_we_have() # This goes through our inventory to see if anything is wearable
            # IDEA: presume certain things are broken if we have them and are not wearing them (login auto wears)
        # We don't even care what happened here, do we, we check "eq" every time fresh
        self.check_if_we_have_broken_stuff_we_can_use() # This just creates self.broken_list. The idea is that we dealt with regex broken_armour which could have been different pieces than DB
        # So we can try repairing...
        self.action_DB_based_broken_list() # This is still to repair not shop (ie. broken list is stuff we have)
        if self.no_gold or self.stopping:
            magentaprint("Armour bot found no gold for DB-based broken list")
            return
            # We can return up with self.broken_list populated... it'll get kept... then when we get run again later we could get the same outcome
        self.go_buy_default_armour() # Now we finally see about buying... this checks "eq" again and buys as necesary

        # self.go_repair_or_replace_broken_armour()
        # Conceivably we start buying replacement armour instead if we have the perfect amount of gold... could be an interesting bug
        # self.get_needed_default_armour()
        # Need to cancel if inventory doesn't have the broken armour piece (user manually repairs armour)

    # def get_needed_default_armour(self):
    def go_buy_default_armour(self):
        # Given size, armor level, slot, choose best piece from shop
        # Ie. steel, medium, neck - plate mail collar
        #desired_items = sorted(self.determine_shopping_list(self.broken_armour), key=lambda item : item.area)
        # We don't need to use broken armour here, since we've been to the smithy.  We should check equipment (I feel uncertain about the order of actions).

        # travel_bot = TravelBot(self.char, self.command_handler, self.map)
        # shopping_bot = ShoppingBot(self.char, self.command_handler, self.map)
        desired_asi_list = self.determine_shopping_list()
        # magentaprint("ArmourBot.get_needed_default_armour() desired_asi_list: " + str(desired_asi_list))

        for asi in desired_asi_list:
            # path = self.map.get_path(self.char.AREA_ID, asi.area.id)
            # travel_bot.follow_path(path)
            # if self.shopping_bot.cant_afford(asi): # Want to keep a higher minimum than 0 gold

            # OK bonus case... suppose we forgot we have it broken? 
            # count = self.inventory.count(asi.item.name)

            # THERE IS NO "HAS" AT THIS POINT

            # Now going to buy it
            if self.char.GOLD < self.gold_to_save_for_weapon + asi.item.value:
                # just skip it and keep running instead of traveling there etc.... take the death risk with no money
                # Also this is the correct time to check because gold can change
                magentaprint("Skipping can't afford to buy {}, need {}+{}, have {}".format(str(asi.item.name), self.gold_to_save_for_weapon, asi.item.value, self.char.GOLD))
                self.no_gold = True # unnecessary as we are just about done
                # Hmmm maybe move this to determine shopping list? No because it might matter if we bought one earlier in the loop
                continue

            magentaprint("ArmourBot.get_needed_default_armour GOING TO GET " + str(asi.item.name))
            # if self.inventory.has(asi.item.name):
            #     self.command_handler.wear.execute_and_wait(self.char.inventory.get_last_reference(str(asi.item.name)))
            #     if not self.command_handler.wear.success:
            #         raise(Exception("Weird armour bot case - shouldn't be trying to buy what we have"))
            self.travel_bot.go_to_area(asi.area.id)
            if self.stopping:
                return
            if self.shopping_bot.buy_from_shop(asi):
                self.command_handler.wear.execute_and_wait(self.char.inventory.get_last_reference(str(asi.item.name)))
                if self.command_handler.wear.result in R.no_room:
                    # This is probably the equipment command messing up and buying unnecessarily
                    # The equipment dict didn't get set up right
                    # self.get_needed_default_armour() 
                    # This will call determine_shopping_list again
                    raise(Exception("Did equipement command screw up??")) # Try exception here
                    # break # This will prevent finishing the current version of the loop
                elif self.command_handler.wear.result in R.not_yet:
                    raise(Exception("Armour bot logic error didn't catch character level too low to wear thing"))
                # if asi.item.name in self.broken_armour:
                #     self.broken_armour.remove(asi.item.name)
                # else:
                #     self.broken_armour = []
                # Presumably we succeeded
                # Could have had can't carry...
                # If we had can't carry then... maybe we just leave it??
                # I wrote code for that once
                # Shopping bot actually REALLY tries... it does all that going selling dropping and trying again
                # I guess it'll give up if it couldn't
                if not self.command_handler.wear.success:
                    raise(Exception("Armour bot failed?"))
            else:
                # TODO: a) check character max weight agains item weight and only travel and buy if the item can be carried
                # or b) go on a vendor/recycling trip and come back
                raise(Exception("Armour bot's shopping bot failed???"))
                pass

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

    def action_existing_broken_list(self):
        # Assume last reference I guess...
        # What if we can't afford it...
        # Well, have a go...

        # Existing broken list is what is known from things that broke that we have regexes for
        # "Action" refers to going to repair them

        to_remove=[]
        for a in self.broken_armour:
            if self.stopping:
                return

            # possible_weapons = self.command_handler.weapon_bot.possible_weapons

            if Item.gold_lookup(a) and self.char.GOLD - Item.gold_lookup(a)/2 < self.gold_to_save_for_weapon:
                magentaprint("Skipping can't afford to repair {}, need {}+{}, have {}".format(a, self.gold_to_save_for_weapon, Item.gold_lookup(a)/2, self.char.GOLD))
                self.no_gold = True # Hmmm why did I even make this variable... we could just keep checking every time, why not... 
                continue
            # elif possible_weapons[-1] == None or possible_weapons[-1].item == None or possible_weapons[-1].item.value == None or self.char.GOLD < 2*possible_weapons[-1].item.value:
                # # I don't think this is possible
                # magentaprint("Armour bot... no info on needed money for weapon... {}, need {}+{}, have {}".format(a, self.gold_to_save_for_weapon, Item.gold_lookup(a)/2, self.char.GOLD))
                # self.no_gold = True
                # continue
                # # Adding it because I removed it from another place where it was making my guy drop all the broken armour
                # # Not a great reason to add it
            else:
                magentaprint("Going to repair {}, needed {}+{}/2, have {}".format(a, self.gold_to_save_for_weapon, Item.gold_lookup(a), self.char.GOLD))

            self.go_to_nearest_smithy() # Even if it's from regex fall apart, we can still check DB for gold lookup and delay deciding to go to the smithy
            # (was going to smithy without enough money)
            # However, even if we don't know the value, we can attempt
            # We'd end up attempting repeatedly...

            try_repair_and_wear_result=self.try_repair_and_wear(self.inventory.get_last_reference(a))

            if try_repair_and_wear_result==True:
                # Ehrm but how do we remove from current list... caller shouldn't do it
                to_remove.append(a)
            elif try_repair_and_wear_result=='no gold':
                magentaprint("Wow couldn't afford{}, need {}+{}/2, have {}".format(a, self.gold_to_save_for_weapon, Item.gold_lookup(a), self.char.GOLD))
                # Okay conceivably something wasn't in the dB... we don't want to abort though...
                # I guess keep going... he might buy or wear a substitute...  then repair and sell this broken thing... 
                self.no_gold=True
                continue
            elif try_repair_and_wear_result=='darnitall':
                to_remove.append(a)
            elif try_repair_and_wear_result=='repair_what':
                # This happened when I stopped the bot and repaired something and then started the bot
                # So, ideally, I guess, Repair command would edit armour_bots state vairables, .broken_armour, .broken_list
                # But this shouldn't happen without user intervention... we can recover - just remove from .broken_list? No, .broken_armour
                magentaprint("Armour_bot2 confused... moving on... ")
                to_remove.append(a)
            else:
                raise(Exception("Armour bot had trouble with repair and wear"))

        for a in to_remove:
            self.broken_armour.remove(a)

    def try_repair_and_wear(self, ref):
        # Does "repair" and "wear" on the item. Keep in mind repairing can delete the item
        repair = self.command_handler.repair
        repair.execute_and_wait(ref)
        if repair.success:
            wear=self.command_handler.wear
            wear.execute_and_wait(ref)
            if wear.success:
                return True
            elif wear.no_room:
                self.inventory.add_to_keep_list_ref(ref) #This case is bananas
            # Pretty sure we needed to wear it... guess we'll have to stop with ring reaction though
        elif repair.no_gold:
            return "no gold"
        elif repair.darnitall:
            return "darnitall"
        elif repair.repair_what:
            return "repair_what"
        else:
            raise(Exception("armour bot 2 was expecting repair to happen normally..."))

    def action_DB_based_broken_list(self):
        to_remove=[]
        for a in self.broken_list:
            if self.stopping:
                return

            if self.char.GOLD - Item.gold_lookup(a)/2 < self.gold_to_save_for_weapon:
                magentaprint("Skipping can't afford to repair {}, need {}+{}, have {}".format(a, self.gold_to_save_for_weapon, Item.gold_lookup(a)/2, self.char.GOLD))
                self.no_gold = True
                continue
            else:
                magentaprint("Going to repair {}, needed {}+{}, have {}".format(a, self.gold_to_save_for_weapon, Item.gold_lookup(a)/2, self.char.GOLD))

            self.go_to_nearest_smithy()

            try_repair_and_wear_result=self.try_repair_and_wear(self.inventory.get_last_reference(a))

            if try_repair_and_wear_result==True:
                # Ehrm but how do we remove from current list... caller shouldn't do it
                to_remove.append(a)
            elif try_repair_and_wear_result=="no gold":
                self.no_gold=True
                continue
            elif try_repair_and_wear_result=="darnitall":
                to_remove.append(a)
            elif try_repair_and_wear_result=="repair_what":
                # This happened when I stopped the bot and repaired something and then started the bot
                # So, ideally, I guess, Repair command would edit armour_bots state vairables, .broken_armour, .broken_list
                # But this shouldn't happen without user intervention... we can recover - just remove from .broken_list? No, .broken_armour
                magentaprint("Armour_bot2 confused... moving on... ")
                to_remove.append(a)
            else:
                raise(Exception("Armour bot had trouble with repair and wear"))

        for a in to_remove:
            self.broken_list.remove(a)

    def try_what_we_have(self):
        magentaprint("try what we have!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        desired_list = self.determine_shopping_list()
        for asi in desired_list:
            for ref in self.inventory.get_reference_for_each_one(asi.item.name):
                # Provided in reverse order
                if self.try_piece_from_inventory(ref):
                    break # It equipped - go to next asi

    def try_piece_from_inventory(self, ref):
        if self.inventory.check_if_broken(ref):
            return

        self.command_handler.wear.execute_and_wait(ref)
        if self.command_handler.wear.success:
            return True
        else:
            magentaprint("Armour bot setting {} to be broken.".format(ref))
            self.inventory.set_broken(ref) # "Wear" could have done this... right?... yeah it's supposed to do it

    # def increment_ref(self, ref, qty=1):
    #     if len(ref.split(' ')) > 1:
    #         return ref.split(' ')[0] + ' ' + str(int(ref.split(' ')[1]) + qty)  # ref++
    #     else:
    #         return ref + ' ' + str(qty + 1)

    def check_if_we_have_broken_stuff_we_can_use(self):
        """ Adds items that we have that are viable to wear to self.broken_list """
        desired_list       = self.determine_shopping_list()
        ref                = ""
        last_asi_item_name = ""
        self.broken_list   = [] # Ok let's do try having two lists... one broken_armour, one broken_list... oooffff whyyy.... broken_armour came from regexes, broken_list is based on DB query
        for asi in desired_list:
            # Suppose we have a few iron rings we need
            # We are iterating through inventory to see if we have some broken and adding the correct amount to broken_list
            if ref:
                # from previous iteration
                if last_asi_item_name == asi.item.name:
                    # If same item is again in desired_list
                    ref=self.inventory.decrement_ref(ref)
                    # MTD=
                    # self.smartCombat.mob_target_determinator.increment_ref(ref)
                    if ref and self.inventory.get_item_name_from_reference(ref) == asi.item.name:
                        pass # good, we have correct item after decrementing ref
                    else:
                        continue # We don't have enough of that item, so do not put in broken_list
                else:
                    # ref="" # We ran out of that item
                    ref = self.inventory.get_last_reference(asi.item.name) # We are on a new item, so set up inital ref (last)
            else:
                ref = self.inventory.get_last_reference(asi.item.name) # See if we have the first one of that item

            if ref:
                self.broken_list.append(asi.item.name) # Yes we have a(nother)? good ref of that item

            # count_have = self.inventory.count(asi.item.name)
            # for ref in self.inventory.get_reference_for_each_one(asi.item.name):
            last_asi_item_name = asi.item.name

        # The stuggle is what if it was wearing something different from what comes up in shopping list
        # Don't we just want to go with that
        # I guess we have to if we want to maintain that function
        magentaprint("armour bot check_if_we_have_broken_stuff_we_can_use got {}".format(self.broken_list))


    # def determine_shopping_list(self, broken_armour):
    def determine_shopping_list(self):
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
        # Plate lower tier steel maybe (not yet adept enough for steel) (large iron shield)
        # Chain: Rangers, assassins, clerics (iron shield)
        # Ring mail: Mages, druids, alchemists, thieves (bone shield)

        self.command_handler.equipment.execute_and_wait()
        desired_items = []

        inventory_copy = ReferencingList(self.inventory.list)

        for slot in self.command_handler.equipment.slot_names:
            if self.command_handler.equipment.dict[slot]:
                continue # Skip equipment slot if are already wearing something

            # Search db for a piece given size, class, slot
            # size  = self.determine_size(self.char.info.race)
            # armour_level = self.determine_armour_level(self.char.class_string)
            # size  = ArmourSizeDeterminator().determine(self.char.info.race)
            # armour_level = ArmourLevelDeterminator().determine(self.char.class_string)
            size  = self.get_size(self.char.info.race)
            armour_level = self.get_armour_level(self.char.info.level)  # checks class and level (low level paladin can't wear steel yet)
            # magentaprint("armour_bot.determine_shopping_list() size: " + size + ", slot: " + str(slot) + ", armour_level: " + str(armour_level))
            if slot == 'wielded' or slot == 'seconded':
                continue
            if slot == 'face' or slot == 'holding':
                continue  # no masks in shops, so this hack will probably stay.  We should add 'face' slot to the db.
            if re.search(r'\d$', slot):
                slot = slot[:len(slot)-1]  # neck2, finger3, etc.
            slot = slot.title()
            # buyable_items = AreaStoreItem.get_by_item_type_and_level_max(size, slot, armour_level)
            buyable_items = AreaStoreItem.get_buyable_armour(size, slot, armour_level) # Returns any possible items for current slot
            # This is a good print... but so large
            # magentaprint("Called get_buyable_armour(size={},slot={},armour_level={}), got {}.".format(size, slot, armour_level, len(buyable_items)))

            #magentaprint("determine_shopping_list() buyable_items: " + str(buyable_items))
            # if buyable_items:
            #     if len(buyable_items) > 0:
            #         magentaprint(str(len(buyable_items)))  # Object of type 'SelectQuery' has no len()
            #         magentaprint("determine_shopping_list() buyable_items[0]: " + str(buyable_items[0]))
            #         magentaprint("determine_shopping_list() buyable_items[0].level: " + str(buyable_items[0].level))
            #         buyable_items.sort(key=lambda item: item.level, reverse=True)
            #         desired_items.append(buyable_items[0])
            # if buyable_items:
            #     buyable_items.sort(key=lambda item: item.level, reverse=True)  # Use the highest armour_level match
            #     # 'SelectQuery' object has no attribute 'sort'  ... maybe it is an iterator though
            #     magentaprint("determine_shopping_list chose " + buyable_items[0].item.name)
            #     desired_items.append(buyable_items[0])
            #dir(buyable_items)
            # magentaprint("ArmourBot determine_shopping_list() size {0}, slot {1}, armour_level {2}, found {3}".format(size, slot, armour_level, str(buyable_items)))
            magentaprint("armour bot got {}".format(buyable_items))

            # index = self.inventory.index(a.item.)

            # (x) This outer any may be somewhat efficient but i think it's better to skip it ... maybe need tests happening this code
            # -- No, it's not redundant because we use the ELSE
            # If we have already any of the desired items in inventory, use that
            # If we don't have any, use buyable_items[0]

            # if any(self.inventory.has(a.item.name) for a in buyable_items):
            if any(inventory_copy.has(a.item.name) for a in buyable_items):
                # That was a pre-check on "has"... maybe slow though (has any) ... but there is an else that's needed
                # That is, "if we have any of buyable_items"
                for item in buyable_items:
                    if inventory_copy.has(item.item.name):
                        # Add the item we have to desired_items, which will trigger repairing, instead of buying something else, which [0] could be
                        desired_items.append(item) 
                        inventory_copy.remove(item.item.name)
                        # Prefer what we have... armour bot will try to repair it or keep using it... if it broke at smithy we can then give a different answer as we won't have it
                        break
                        # Suppose we have a steel ring and an iron ring...
                        # Ok I think I can handle this (inventory_copy)
                        # Now, .has can be false, so, iron ring and steel ring could both end up in desired_items and therefore keep list
            else:
                # If we didn't have any in inventory, then we can add anything buyable we found (xxx)
                # Add restrictions to not over buy at low level
                if buyable_items:
                    if self.char.info.level==1:
                        pass # Don't buy armour at level 1, leveling is only 64g I think
                    elif self.char.info.level==2: # && 'leather jerkin' in [b.item.name for b in buyable_items]:
                        # desired_items.append
                        # pass # Even leather jerkin is a money sink at level 2
                        for b in buyable_items:
                            if b.item.name == 'studded leather leggings':
                                desired_items.append(b) # Just testing a recent fix
                                break; # So we only add one item for the slot
                                # Probably suboptimal to buy even this at level 2 but let's buy one armour for fun
                                # Bot could struggle with gold at level 2 if it has bad combat stats
                    elif self.char.info.level==3:
                        for b in buyable_items:
                            if b.item.name in ['leather jerkin']:
                                desired_items.append(b)
                                break; # So we only add one item for the slot
                                # Yeah do need to drop the money drains at low level, to be able to buy long sword, or to level up gold is needed, expenses down like repairs
                    elif self.char.info.level==4:
                        for b in buyable_items:
                            if b.item.name in ['hard cap', 'hard boots', 'studded leather gloves', 'lacquered wooden shield', 'studded leather leggings', 'studded leather sleeves', 'studded leather armour']:
                                desired_items.append(b)
                                break; # So we only add one item for the slot
                                # leave out iron ring
                                # The idea here is that we don't want to buy so much armour that the guy can't make gold net positive eventually... or afford a decent weapon...
                    else:
                        desired_items.append(buyable_items[0]) # This adds the first one in buyable_items
                        # If level >= 4 any armour in the dB is fair game
                        # Test code btw is 
                        # exec print(AreaStoreItem.get_buyable_armour(self.armour_bot.get_size('Dwarf'), 'Body', 1))
                        # and armour_init
            # Why not just add it regardless?
            # Because we want to add what we have first, which may not be [0]
            # 

            # for item in buyable_items:
            #     # magentaprint("Won't print if there's no valid item: " + str(item))
            #     # Don't bother sorting for now
            #     desired_items.append(item)
            #     magentaprint("armour appended {}".format(item)) # Yeah we are clobbering result here, we're only taking the top result... because "break"
            #     break

        # Ok fair to say... we don't want to spend too much on armour at level 2...
        # Leveling costs 128g... maybe he'll get there eventually... or will he forever spend all his money on hard caps and gloves and boots...

        #magentaprint("Armour bot shopping list " + str(desired_items))
        # magentaprint("Armour bot shopping list: \n" + str([asi.item.name for asi in desired_items]))
        magentaprint("ARMOUR BOT SHOPPING LIST: [\n" + "\n".join("    {} {}".format(asi.item, asi.item.name) for asi in desired_items)+']')
        magentaprint("Race: {}; Size: {}; Armour_level: {}".format(self.char.info.race, self.get_size(self.char.info.race), self.get_armour_level(self.char.info.level)))
        return desired_items
        # TODO: One issue: shields aren't sized - so queries that use any size need to return the shield, whose type may be
        # the generic armour type.   SELECT "t1"."id", "t1"."area_id", "t1"."item_id" FROM "areastoreitem" AS t1 INNER JOIN "item"
        # AS t2 ON ("t1"."item_id" = "t2"."id") INNER JOIN "itemtype"
        # AS t3 ON ("t2"."itemtype_id" = "t3"."id") WHERE (("t2"."level" <= ?) AND (("t3"."model_id" = ?) AND ("t3"."data_id" = ?)))

        # for slot in ['body','arms','legs','neck1','neck2','face','hands','head', 'shield']:

    def go_repair_or_replace_broken_armour(self):
        # These functions can unset self.broken_armour if they successfully wear a piece
        # And they operate on self.broken_armour

        # if self.do_for_each_broken_piece(self.try_armour_from_inventory):
        #     return

        self.do_for_each_broken_piece(self.try_armour_from_inventory)

        # if any(a in [i.name for i in self.inventory.list] for a in self.broken_armour):
        # if self.broken_armour:
        # if any(a in [i.name for i in self.inventory.list] for a in self.broken_armour):
        # if any(Item.gold_lookup(a)  in [i.name for i in self.inventory.list] for a in self.broken_armour):
        if any(a in [i.name for i in self.inventory.list] and self.char.GOLD - Item.gold_lookup(a)/2 >= self.gold_to_save_for_weapon for a in self.broken_armour):
        # if any(a in [i.name for i in self.inventory.list] for a in self.broken_armour if Item.gold_lookup()):
            # (^ if we have one of that item in the inventory)
            # Can we add "if there's an asi for it and we have a gold estimate"
            # I guess, maybe, areastoreitem.gold_lookup(item_name)... but that's a loop of DB queries then... but it's a loop over a super short list so it's fine
            self.go_to_nearest_smithy()

        self.do_for_each_broken_piece(self.repair_and_wear)
        # self.do_for_each_broken_piece(self.go_buy_and_wear)  # I think we'll skip this bit and rely on the default armour
            # We should make all the paths beforehand to ensure an efficient shopping trip
        self.broken_armour = []  # If it couldn't be repaired, it's time to forget about it (use default armour not try to maintain what was worn)

        # self.broken_armour = self.try_armour_from_inventory(self.broken_armour[:])
        # self.go_to_nearest_smithy()
        # self.broken_armour = self.repair_and_wear_armour_from_inventory(self.broken_armour[:])
        # self.broken_armour = self.go_buy_and_wear_armour(self.broken_armour[:])

    @property
    def gold_to_save_for_weapon(self):
        return 2*self.command_handler.weapon_bot.possible_weapons[-1].item.value

    def do_for_each_broken_piece(self, function):
        list_copy = self.broken_armour[:]

        for a in self.broken_armour:
            if a:
                if function(a):
                    list_copy.remove(a)

        self.broken_armour = list_copy

    def try_armour_from_inventory(self, a):
        # We are going to try "wear" on all of this kind of armour from the inventory (in reverse order)
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

        # Caller removes it from self.broken_armour in do_for_each_broken_piece()

    def repair_and_wear(self, a):
        # So "a" is a string from the armour that broke and we use get_last_reference to get that piece
        # That means we can't check the price
        # So if the bot has a bunch of armour it could lose money and stop working
        # It only buys armour is it has enough
        # I guess we could just weaken this clause for now, make it 3x weapon cost

        # We'll do a gold check here because this is where we've decided to go through with a specific armour
        # if self.char.GOLD < 2*self.command_handler.weapon_bot.possible_weapons[0].item.value + a.item.value:
            # UMMM 'a' is a string!
        # if self.char.GOLD < 3*self.command_handler.weapon_bot.possible_weapons[-1].item.value:
        if self.char.GOLD - Item.gold_lookup(a)/2 < self.gold_to_save_for_weapon:
            magentaprint("Armour bot decided we don't have enough gold to repair "+str(a))
            return False # This tells the caller it didn't happen so the caller doesn't action it in any lists or inventory
            # I guess this could make for a lot of traveling (should be fixed, added a check above)

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
                elif self.command_handler.repair.result in R.cant_repair:
                    # This can happen if the character was wearing something odd, so don't raise an exception
                    # ie. big nose and glasses, sticky salve
                    # Caller will remove it from the broken list
                    return True
                else:
                    magentaprint("Confused ArmourBot.")
                    # Could try go to smithy again here if necessary
                    # "It's not broken yet".... well my command was wrong... steel 3 not steel 2...
                    # That was from assuming in try_armour_from_inventory that the last ref was going to be the broken one
                    # I think no_gold gets us here
                    raise
        else:
            magentaprint("ArmourBot.repair_and_wear() error - no inventory ref for " + str(a) + ".")  
            # Todo? What if the armour fell apart... then it's not in inventory...

    def go_buy_and_wear(self, a):
        # I think we won't try to shop for the same armour that just broke, and just fall back immediately to the default set
        pass

    # def cant_afford(self):
    #     # shopping_bot cant_afford is similar
    #     # (I guess armour_bot is not using shopping bot? It kind of is...??)
    # def cant_afford(self, asi):
    #     # Item.get_item_by_name(asi.item
    #     if asi.item.value:
    #         return asi.item.value > self.char.GOLD
    #     else:
    #         magentaprint("Warning: Database should really have 'value' (cost) assigned for " + asi.item.name)
    #     # return asi.get_cost() > self.char.GOLD


    # def go_to_nearest_smithy(self, grinding=False):
    #     magentaprint("TopDownGrind.go_to_nearest_smithy()")
    #     smithy_path = self.get_smithy_path()
    #     magentaprint("TopDownGrind.get_smithy_path(): " + str(smithy_path))
    #     self.travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.map)
    #     self.travel_bot.follow_path(smithy_path)


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
        if self.steel_class():
            if character_lvl > 9:
                # Bard confirmed can't wear steel gauntlets at level 8 - not adept enough
                # So the bard can wear plate and is not adept enough to wear steel
                # Apparently Druid can wear plate but not steel even at level 10 (need to figure that out - is level the important factor?)
            #     return 5 # Ehrm the dB only has 3 levels right now... can be changed though
            # elif character_lvl > 6: # TODO: set this number correctly
            #     return 4 # plate... what level can it be worn??? Not fighter level 1! 
            # elif character_lvl > 5: # TODO: set this number correctly
                return 3  
                # Ehrm wonder how many actual armour levels there are in the game... maybe just 3??
                # I think unlocking steel at level 10 is correct? Also steel being level "3"
            elif character_lvl > 4: # OK yes I believe at level 5 barbarian "unlocked" chain mail... how about steel?
                return 2 # Ruorg can wear chain but not steel, right? That'd be level 2
            else:
                return 1 
            # Notes... fighter can't wear chain boots nor plate collar at level 1
            # level 4 Dwarf barbarian couldn't wear chain mail boots
            # Another note: "Some chain mail boots doesn't fit you." does come in if they don't fit, over "You are not yet adept enough to use this!"
        elif self.chain_class():
            if character_lvl > 9:
                return 2 # Was 3 and ruorg tried to buy a steel collar...
            else:
                return 1 # ring mail... but can mages wear ring mail hmmm
        else:
            return 1

    def get_size(self, race):
        if race.lower() in ['hobbit','halfling','gnome','dark-elf','dwarf']:
            return 's-armor'
        elif race.lower() in ['human','half-elf','half-orc','elf']:
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
    def chain_class(self):
        return self.char.class_string in ['Alc', 'Thi', 'Dru', 'Ran', 'Cle', 'Ass']
    def steel_class(self):
        #magentaprint("ArmourBot.steel_class() class string is: " + str(self.char.class_string))
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


