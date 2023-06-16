
import time, re, collections

from Exceptions import *
from misc_functions import *
import comm.RegexStore as R
from command.Command            import SimpleCommand
from db.MudItem                 import MudItem
from reactions.referencing_list import ReferencingList

def clip_in_your_off_hand(wield_string):
    # Example wield_string: a spear in your off hand
    wield_string = wield_string.replace('\n\r', ' ')
    length = len(wield_string)

    if wield_string[length-17:length] == " in your off hand":
        return wield_string[:length-17]
    else:
        return wield_string

def clip_from_a_container(get_string):
    # Example get_string: some chicken soup from a sack
    get_string = get_string.replace('\n\r', ' ')
    M = re.search("(.+?) from (.+?)", get_string)
    if M:
        return M.group(1)
    else:
        return get_string

def construct_items(string_list):
    items = []

    try:
        for i in string_list:
            item = MudItem(i)
            item.map()
            items.append(item)
    except:
        magentaprint("inventory database error, something didn't map properly", False)
        pass

    return items

def parse_item_names(item_string_list):
    # returns a list of strings (MudItems can be constructed outside)

    return_list = []
    item_string_list = item_string_list.replace("\n\r", ' ')
    inv_list = item_string_list.split(',')
    inv_list = [item.strip(' \t\n\r') for item in inv_list]
    singles = ['a ', 'an ', 'some ']
    numbers = ['two ', 'three ', 'four ', 'five ', 'six ', 'seven ',
               'eight ', 'nine ', 'ten ', 'eleven ', 'twelve ', 'thirteen ', 'fourteen ',
               'fifteen ' , 'sixteen ', 'seventeen ', 'eighteen ', 'nineteen ', 'twenty ']
    numbers.extend([str(i) + " " for i in range(21, 200)])

    for item in inv_list:
        if (item.endswith(' gold coin') or 
            item.endswith(' gold coins') or 
            item.endswith(' platinum coins') or 
            item.endswith(' silver coins') or
            item.endswith(' rare coins') or 
            item.endswith(' white chips') or
            item.lower() in [
                'gold coins', 
                'platinum coins', 
                'silver coins', 
                #'rare coin',  # Boris Ironfounder
                'white chip', # Floor Manager
                'black chip', # Floor Manager
                'silver chest', 
                'small jade fragment', 
                'amethyst gem']):
            continue
        #if item.endswith(" platinum coins"):  
        # (Misses "The auctioneer was carrying: 13 gold coins, a gavel, platinum coins.")
        # One platinum coin comes in as "platinum coins" 
        # (without a quantifier, so the preceding space got stripped).

        if not any(item.startswith(s) for s in singles + numbers):
            return_list.append(item)  # ie 'maul hammer'
            continue

        if any(item.startswith(s) for s in singles):
            return_list.append(item.partition(' ')[2])  # ie 'a maul hammer'
            continue

        for n in range(0, len(numbers)):
            number = numbers[n]
            if item.startswith(number):
                item = item[len(number):]

                if item.startswith("sets of"):
                    item = item.replace("sets of ", "")
                elif (item.endswith('ses') or item.endswith('xes')) and not item.endswith('axes'):
                    item = item[:len(item)-2]
                elif item.endswith('s'):
                    item = item[:len(item)-1]

                return_list.extend([item]*(n+2))

    # magentaprint("parse_item_names from {0}  got  {1}".format(item_string_list, return_list))
    return return_list
    # Two sets of plate mail leggings
    # some plate mail leggings
    # So don't remove the plural s if it started with sets of

def parse_item_list(inventory_string):
    return construct_items(parse_item_names(inventory_string))

def parse_item_list_dict(inventory_string):
    ''' Returns a dict {item: quantity} ie. {"chicken soup": 5, steel bottle: 1} '''
    return_dict = {}
    inventory_string = inventory_string.replace("\n\r", ' ')
    # inventory_string = inventory_string.replace("  ", ' ') #replace double space with a single one
    inv_list = inventory_string.split(',')
    inv_list = [item.strip(' \t\n\r') for item in inv_list]
    singles = ['a ', 'an ', 'some ']
    numbers = ['two ', 'three ', 'four ', 'five ', 'six ', 'seven ',
               'eight ', 'nine ', 'ten ', 'eleven ', 'twelve ', 'thirteen ', 'fourteen ',
               'fifteen ' , 'sixteen ', 'seventeen ', 'eighteen ', 'nineteen ', 'twenty ']  # isn't it '20'?
    numbers.extend([str(i) + " " for i in range(21, 200)])

    for item in inv_list:
        number_found = False
        gold_coin_match = re.match("(\d+) (?:gold|silver) coins?", item)
        if gold_coin_match:
            # add_to_dict(return_dict, 'gold coin', int(gold_coin_match.group(1)))
            continue
        for s in singles:
            if item[0:len(s)] == s:
                number_found = True
                add_to_dict(return_dict, item[len(s):], 1)
                break
        if number_found:
            continue
        for n in range(0, len(numbers)):
        # for number in numbers:
            number = numbers[n]
            if item[0:len(number)] == number:
                number_found = True
                if "sets of" in item:
                    item = item.replace("sets of ", "")
                item = item[len(number):]
                # if item[len(item)-1] == 's':
                if item.endswith('ses') or item.endswith('xes'):
                    item = item[:len(item)-2]
                elif item.endswith('s'):
                    item = item[:len(item)-1]

                    # mud_item = MudItem(item)
                    # mud_item.map()
                    # # mud_items = []
                    # # for _ in range(n - 1):
                    # #     mud_items.append(mud_item)
                    # # item_list = GenericMudList(mud_items)
                    # item_list = GenericMudList([mud_item] * (n - 1))
                    # return_dict[mud_item] = item_list
                add_to_dict(return_dict, item, n+2)
                break
        if number_found is False:
            magentaprint("Inventory parsed " + item)
            #if the item wasn't received with a/an/some etc...
            #we assume it's just one item
            # mud_item = MudItem(item)
            # mud_item.map()
            # item_list = GenericMudList([mud_item])
            # return_dict[mud_item] = item_list
            add_to_dict(return_dict, item, 1)

    return return_dict

def add_to_dict(d, item_str, qty):
    mud_item = MudItem(item_str)
    mud_item.map()
    d[mud_item] = GenericMudList([mud_item] * qty)

# class RegexMatch(object):
#     def __init__(self, regex, M_obj):
#         self.regex=regex
#         self.M_obj=M_obj
# Note that the match object actually holds regex info

class Inventory(SimpleCommand, ReferencingList):
    command = 'i'
    keep_list = [
        # Quest/Trade Items
        'Rod of Ruin', 'bank bond',
        'wrapped scroll', 'wyvern\'s sting', 'gold block', 'gold wand', #'makeup kit', 
        'diamantium cross', 'rare coin', 'silver flute',
        'copper thieves pass', 'bronze thieves pass', 'steel thieves pass', 'silver thieves pass',# 'stilleto'
        'druid\'s silver sickle', 'protective robes', "alchemist's ring",
        'stone medal', 'basilisk scale', 'basilisk head', 'occultate stone', 'jade block', 'rock wolf fang',
        'enchanted indigo cloak', 'fine elven cloak', 'light elven cloak', 'lion charm', 'poison ring', 
        'greenwood jerkin',"paladins's plate armour", "master's habit", 
        'lucky pebble',"blue ioun stone","stolen contract",
        
        # important potions
        'Elixir of Morinva', 'granite potion', 'large granite potion', 'philtre of perception', 'philtre of health',
        'burnt ochre potion', 'chequered vial', 'misty potion',
        'orange potion', # levitate
        'golden potion', #'platinum crucifix', # Helps disease? Worth a lot of money?
        'small flask', 'large restorative', 'scarlet potion',
        'silver chalice', 'steel bottle', 'glowing potion', 'milky potion',

        # containers
        'large sack', 'black bag',

        # super rare weapons/armor
        'dwarven rune hammer', 'silver ram staff', 'true blade', 'mithril war hammer',
        "dragon scale armour", 'monk hammer', 'gauntlets of dexterity',
    ]
    def __init__(self, telnetHandler, character):
        # I am now thinking that inventory is only concerned about the backpack, not what is equipped.
        self.regex_cart = [
            R.you_have          ,
            R.no_inventory      ,
            R.you_get           ,
            # R.you_drop          ,
            R.you_give          ,
            R.you_put_in_bag    ,
            R.not_empty         ,
            R.gave_you          ,
            R.bought            ,
            R.you_hold          ,
            # R.disintegrates     ,
            R.sold              ,
            R.not_a_pawn_shop   ,
            R.wont_buy          ,
            R.wont_buy2         ,
            R.you_wield         ,
            # R.you_wear          ,
            R.nothing_to_wear   ,
            R.you_remove        ,
            R.nothing_to_remove ,
            R.weapon_break      ,
            R.weapon_shatters   ,
            R.armour_breaks     ,
            R.current_equipment ,
            R.gold_from_tip     ,
            R.you_now_have      
        ]
        SimpleCommand.__init__(self, telnetHandler)
        ReferencingList.__init__(self)
        self.character = character
        self.gold = 0
        self.__stopping = False
        self.is_bulk_vendoring = False
        self.equipped_items = {}
        #self.already_removed_dropped_item = False
        # equipped_items = {'body': [], 'arms':[], 'legs':[],'neck':[],'hands':[],'head':[],'feet':[],'face':[],'finger':[],'Shield':[],'Wielded':[],'Second':[]}

        for index, item in enumerate(self.keep_list):
            self.keep_list[index] = MudItem(item)

        self.aura_pot = [
            'chequered vial', 'misty potion'
        ]
        self.granite_pot = [
            'granite potion'
        ]
        self.large_restoratives = [
            'scarlet potion', 'philtre of health', 'tree root' #, 'golden potion'
        ]
        self.restoratives = [
            'chicken soup', 'small restorative', 'white potion', 'small flask', 'large restorative'
        ] + self.large_restoratives
        # , 'tree root']

        self.combat_items = []
        self.__sell_function = False
        self.__drop_function = False
        #self.__previous_regex = None
        self.__return_buffer = [] # List of (regex,M_obj) pairs needed when the command that was sent is needed together with the reply

    # def push_return_buffer(self, regex, M_obj):
    #     #self.__return_buffer.append({'regex':regex,'M_obj':M_obj})
    #     self.__return_buffer.append(M_obj)

    def notify(self, regex, match):
        # magentaprint("\nInventory notify pattern: " + match.re.pattern)
        # magentaprint("Inventory notify got:" + match.group(0))
        if regex in R.you_have:
            # magentaprint('Inventory you_have item list: ' + match.group(1))
            self.set_inventory(match.group(1))
            # magentaprint(str(self.list))
            #magentaprint(str(self.to_dict()))
            #magentaprint(self)
        elif regex in R.no_inventory:
            magentaprint("Inventory no_inventory", False)
            self.items = []
        elif regex in R.sold:
            self.gold = self.gold + int(match.group(1))
            # Do nothing on "wont_buy" except set the wait flag (super)
            if self.__sell_function:
                # We will remove the item from the scope where we know the command that was sent (self.sell)
                self.__return_buffer.append(match)
            # else:
            #     self.remove_many(match.group(2))
            #     (Ok do not remove if it's not self.sell... we used to do this... now we have Sell object calling remove on us)
            # Put Sell object in charge of this removal
        elif regex in R.you_now_have + R.gold_from_tip:
            self.gold = int(match.group(1))
        elif regex in R.you_wield and not match.group('weapon').endswith('in your off hand'):
            self.equipped_items['Wielded'] = [MudItem(match.group('weapon'))]
            magentaprint('Inventory just put object into equipment: ' + str(self.equipped_items['Wielded'][0].obj.name))
            # self.remove_many(weapon) # Wield does this part now
            # self.get_equipment()
        elif regex in R.off_hand:
            self.equipped_items['Second'] = [MudItem(match.group('weapon'))]
            # self.remove_many(weapon) # Second does this part now
            # self.get_equipment()
        elif regex in R.you_get:
            self.add(clip_from_a_container(match.group('items')))
        elif regex in R.you_drop:
            magentaprint("Droppping " + str(match.group(1)), False)
            # Problem: we don't know which item was dropped, so it's hard to keep track of is_usable
            # Maybe we just want to reset everthing after dropping... or the bot needs to manage things,
            # or inventory needs full control of many commands (drop, sell...) ... hmph ... preferring to
            # ask the server
            # No we can do blocking calls to sell and drop from the bot
            # Remove the item from the reaction if necessary
            # But if we are in self.sell/drop and waiting, may as well do it right
            # Ok solution is to save the match to self and deal with it in drop function after the wait call
            # Other solution would be to save the command to self and deal with it here
            # The plan is to have inventory do a blocking call to Sell...
            # (Sometimes we don't like blocking calls...)
            # Ok so store the command that was sent
            #if self.already_removed_dropped_item:
                #self.already_removed_dropped_item = False
            #else:
                #self.remove_many(match.group(1))
            if self.__drop_function:
                pass
            else:
                # self.remove_many(match.group(1))
                pass # Use drop command object
        # elif regex in R.you_give + R.you_put_in_bag + R.disintegrates + R.you_drink:
        elif regex in R.you_give + R.you_put_in_bag:
                self.remove_many(match.group(1))
        # elif regex in R.you_wear + R.you_hold:
        elif regex in R.you_hold:
            self.remove_many(match.group(1))
            #self.get_equipment()
            #we know this is armour of some kind so we need to find a way to assign it to the right spot
        elif regex in R.you_remove + R.gave_you:
            self.add(match.group(1))
        elif regex in R.bought:
            pass
            # if not self.is_bulk_vendoring:
            #     self.get_inventory()  # There are some notes about this at the bottom
            #     # I don't like this very much! I can't use ! to buy a lot of a things.
        elif regex in R.weapon_break + R.armour_breaks:
            magentaprint('Inventory weapon / armour break')
            item = match.group(1)
            self.add_broken(match.group(1))
            # self.get_equipment()
            self.unequip_weapon(item)
        elif regex in R.weapon_shatters:
            magentaprint('Inventory weapon_shatters')
            item = match.group(1)
            self.unequip_weapon(item)
        elif regex in R.current_equipment:
            # Todo: Delete this, since it triggers when looking at another player
            # (it works for 'l self' but not for 'eq')
            character_name = match.group(1)
            equipment_list = re.findall(R.wearing[0], match.group(2))

            if character_name == self.character.name:
                for slot in equipment_list:
                    if slot[0] not in self.equipped_items:
                        self.equipped_items[slot[0]] = []

                    self.equipped_items[slot[0]].append(MudItem(slot[1]))
            # magentaprint(self.equipped_items,False)
        # magentaprint(self.list, False)
        super().notify(regex, match)
        # magentaprint("Inventory notify completely done.")

    def get_inventory(self):
        # magentaprint('\n' + str(self.list))
        # self.clear()
        # self.telnetHandler.write('i')
        # self.wait_for_flag()
        self.execute_and_wait() # Will get notify on You have and super.notify() for the threading event
        magentaprint("get_inventory() got {0}".format(self.list))
        return self.list # Is this reliable? How did we get 'the' in the inventory
        # I have actually get_inventory() got [] right off the bat

    # def get_equipment(self):
    #     return
        # self.telnetHandler.write("l ' + self.character.name)
        # self.wait_for_flag()

    # def has(self, mud_item_string):
    #     mud_item = MudItem(mud_item_string)
    #     mud_item.map()

    #     if self.inventory.count(mud_item) > 0:
    #         return True

    #     return False

    def has_aura_pot(self):
        return any([self.has(r) for r in self.aura_pot])

    def count_aura_pots(self):
        return sum(self.count(r) for r in self.aura_pot)

    def count_granite_pots(self):
        return sum(self.count(r) for r in self.granite_pot)

    def has_restorative(self):
        return any([self.has(r) for r in self.restoratives])
    def has_large_restorative(self):
        return any([self.has(r) for r in self.large_restoratives])

    def count_restoratives(self):
        return sum(self.count(r) for r in self.restoratives)

    def count_small_restoratives(self):
        return sum(self.count(r) for r in self.restoratives if r not in ['large restorative', 'scarlet potion'])

    def count_large_restoratives(self):
        return sum(self.count(r) for r in self.restoratives if r in ['large restorative', 'scarlet potion'])

    def has_any(self, item_name_list):
        # if item_name_list.__class__ == 'str':
        if item_name_list.__class__ != [].__class__:
            raise Exception("Inventory.has_any() argument must be a list")
        return any([self.has(i) for i in item_name_list])

    def has_broken(self, item_name):
        if item_name.__class__ != ''.__class__:
            raise Exception("Inventory.has_broken() argument must be a string")
        return any([not i.usable for i in self.get_all_by_name(item_name)])

    def get_broken(self, item_name):
        if item_name.__class__ != ''.__class__:
            raise Exception("Inventory.get_broken() argument must be a string")
        # return [not i.usable for i in self.get_all_by_name(item_name)].index(True)
        # return self.inventory.list.index(item_name)
        # return [not i.usable for i in self.get_all_by_name(item_name)].index(True)
        return self.get_reference_from_index([i.name == item_name and not i.usable for i in self.list].index(True))

    def has_unbroken(self, item_name):
        # Note that this isn't trustworthy until Sell is fixed to remove the correct item
        if item_name.__class__ != ''.__class__:
            raise Exception("Inventory.has_broken() argument must be a string")
        if any([i.usable for i in self.get_all_by_name(item_name)]):
            return True

    def get_unbroken(self, item_name):
        if item_name.__class__ != ''.__class__:
            raise Exception("Inventory.get_broken() argument must be a string")
        # return [not i.usable for i in self.get_all_by_name(item_name)].index(True)
        # return self.inventory.list.index(item_name)
        # return [not i.usable for i in self.get_all_by_name(item_name)].index(True)
        return self.get_reference_from_index([i.name == item_name and i.usable for i in self.list].index(True))

    def has_any_broken(self, item_name_list):
        if item_name_list.__class__ != [].__class__:
            raise Exception("Inventory.has_any_broken() argument must be a list")

        for n in item_name_list:
            if self.has_broken(n):
                return True

    def has_slot_equipped(self, slot_to_check, quantity=1):
        has_slot_equipped = False

        for slot in self.equipped_items:
            magentaprint(slot)
            if slot == slot_to_check:
                magentaprint(str(self.equipped_items))
                if len(self.equipped_items[slot]) >= quantity:
                    has_slot_equipped = True
                    break

        return has_slot_equipped

    def get_usable_item_of_type(self, item_model, item_data, level=1):
    #     return self.inventory.get_object_of_type(itemModel, itemData, level)
        return self.get_usable_object_of_type(item_model, item_data, level)

    # def use(self, item_or_list):
    #     item = ""
    #     if type(item) is list:
    #         for i in item_or_list:
    #             if i in self.inventory:
    #                 item = i
    #                 break
    #     else:
    #         item = item_or_list
    #     self.telnetHandler.write("use " + item)
    #     # Inventory.remove_from_qty_dict(self.inventory, (item, 1))
    #     self.remove(item)
    # the following version has 'usable' error checking
    # def use(self, item, target=None):
    #     if item in self.usable:
    #         if target:
    #             self.telnetHandler.write("use " + item + " " + target)
    #         else:
    #             self.telnetHandler.write("use " + item)
    #     else:
    #         magentaprint("Inventory: Error: " + item + " not usable.")
    #             self.telnetHandler.write("use " + item)

    def sell_stuff(self):
        self.__stopping = False
        # self.get_inventory()  # Unnecessary if inventory is well tracked
          # also - sellable does this

        for item_ref in self.sellable():
            if not self.__stopping:
                self.sell(item_ref)
            else:
                return

    def sell(self, item_ref):
        magentaprint("Inventory.sell deprecated!")
        self.__sell_function = True
        self.telnetHandler.write("sell " + item_ref)
        self.wait_for_flag() 
        # return_regexes=[m.pattern for m in self.__return_buffer]:
        # if R.sold in return_regexes:
        #     # Need m or to remove the m with this pattern
        # elif R.wont_buy in [m.pattern for m in self.__return_buffer] or R.wont_buy2 in :
        for m in self.__return_buffer:
            #if m.re.pattern in R.sold + R.wont_buy + R.wont_buy2:
            if m.re.pattern in R.sold:
                self.remove_by_ref(item_ref)
                self.__return_buffer.remove(m)
                break
            #elif m.re.pattern in R.wont_buy + R.wont_buy2:
        self.__sell_function = False
        # Ok we don't know which item got sold... assuming that the last one got sold would be better
        # Bot selling we can assume it's the last one since the bot sells in reverse order
        # User selling... could use a Sell object...
        # Bot should probably use a Sell object...
        # Right here, do a blocking call, then remove the correct item using item_ref instead of with the reaction
        # (Getting the right one can help if one is broken)
        # Eh did this ever work? Now we have a sell object that will tell us what happened.

    def bulk_sell(self, item_string, quantity):
        magentaprint("Bulk selling: " + item_string + " #" + quantity)
        self.is_bulk_vendoring = True
        i = 0

        while i < quantity:
            self.sell(item_string)
            i += 1

        time.sleep(3) #breathe!
        self.is_bulk_vendoring = False

    def buy_stuff(self, item_string):
        #this should be implemented to match sell stuff
        #programmatic purchasing via a shopping list or something
        return

    # Add print to whenever an item is added, because we got 'the' added somehow
    # Then we are ok to start it with a print
    # And we can do the Event thing (modify _waiter flag assignments to .set())

    def buy(self, item_string):
        self.telnetHandler.write("buy " + item_string)
        self.wait_for_flag()
        self.add(item_string)

    def bulk_buy(self, item_string, quantity):
        i = 0
        self.is_bulk_vendoring = True

        while i < (quantity ):
            self.telnetHandler.write("buy " + item_string)
            i += 1

        time.sleep(3) #breathe!

        self.is_bulk_vendoring = False

    def bulk_give(self, item_string, target, quantity):
        i = 0

        while i <= (quantity):
            self.telnetHandler.write("give {} {}".format(item_string, target))
            i += 1

        time.sleep(3) #breathe!

    # def sell_fast(self):

    def drop_stuff(self):
        magentaprint("Inventory.drop_stuff() (Don't use this! Can mixes up which items of same name are broken.)")
        self.__stopping = False
        # self.get_inventory()  # Maybe unnecessary, except I see "You don't have that" if removed

        for item_ref in self.sellable():
            if not self.__stopping:
                self.drop(item_ref)
            else:
                return

        for item_ref in self.droppable():
            if not self.__stopping:
                self.drop(item_ref)
            else:
                return

    def drop(self, item_ref):
        # Ok let's not trust the reaction to do the removal, since it doesn't know the command that was sent, like sell
        # But we need to know what happened!
        # Do we have a previous regex variable?
        # There is a thread trade happening
        self.__drop_function = True
        self.telnetHandler.write("drop " + item_ref)
        self.wait_for_flag()
        self.remove_by_ref(item_ref)
        self.__drop_function = False

    def drop_last(self, item_string):
        # item_ref = self._item_string_to_reference(item_string)  # TODO: This looks like it would crash
        item_ref = self.get_last_reference(item_string)
        self.telnetHandler.write("drop " + item_string  + " " + str(position))
        self.wait_for_flag()

    def bulk_drop(self, unique_word, qty):
        # item_ref = self.get_first_reference(unique_word)
        for i in range(qty):
            #self.already_removed_dropped_item = True
            #self.telnetHandler.write("drop " + unique_word)
            #self.wait_for_flag()
            #self.remove_by_ref(unique_word)
            self.drop(unique_word) # Drop will remove by ref now (don't need already_removed_dropped_item)

    def stop(self):
        self.__stopping = True

    # def add(self, mud_item):
    #     # for obj, qty in obj_dict.items():
    #     self.inventory.add({mud_item, GenericMudList[mud_item]})

    #     # magentaprint("MudObjectDict added " + str(obj_dict.keys()))
    #     # self.sort()
    #     # pass

    # def add(self, item_string):
    #     # Unfortunately there are a few (three) formats to keep track of.
    #     # ReferencingList isn't smart enough to make objects, so we have to overwrite add.
    #     # We sometimes add MudItems, we sometimes add strings from the mud, and we sometimes
    #     # want to add items by name.
    #     self.add_by_string_list(self.parse_item_names)

    def add(self, item_string):
        magentaprint("Inventory.add %s parses as %s." % (item_string, str(parse_item_list(item_string))))
        items = parse_item_list(item_string)  # This is overloaded for "hammer" and "a hammer"
        for i in items:
            # magentaprint("[" + i.name + "] #" + str(len(i.name)), False)
            #     magentaprint("Trying to add a really long item added - maybe we shouldn't do that?? " + i.name, False)
            # else:
            # magentaprint("Inventory adding %s" % str(i))
            super().add(i)  # Turn it into a MudItem?

    def add_broken(self, item_string):
        items = parse_item_list(item_string)

        for i in items:
            i.usable = False
            super().add(i)

    def add_broken_to_dict(self, item_string):
        # items = parse_item_list(item_string)

        # for name, qty in items:
        #     for i in range(0,qty):
        #         item = MudItem(name)
        #         item.is_unusable = True
        #         self.add(item)
        # for name in item_string: # separates out letters...
        for itemkey, itemlist in parse_item_list_dict(item_string).items():
            for item in itemlist:
                self.add(item.to_string())
                magentaprint("Inv add broken on ref " + self.get_last_reference(item.to_string()))
                self.set_broken(self.get_last_reference(item.to_string()))
                # This is something crazy like O(n^4) but I'm having a hard time...
                # so I'm avoiding constructing MudItem, GenericMudList, MudObjectDict in order to avoid adding to
                # MudObjectDict one at a time.  Its add function requires another dict as input.

    def set_broken(self, ref):
        self.unset_usable(ref)

    def set_inventory(self, item_string):
        # self.inventory = MudObjectDict()
        # self.inventory.add(parse_item_list_dict(item_string))
        # self.inventory = MudObjectDict().add(parse_item_list_dict(item_string))  # constructor doesn't return self

        # d = MudObjectDict()
        # d.add(parse_item_list_dict(item_string))
        # # This overwrites all state information (is_unusable), so only overwrite when the new dict is somehow different.
        # if not self.compare_mud_object_dicts(d, self.inventory):
        #     self.inventory = d

        # remove magic and alc enchanted items
        item_string = re.sub(" \(.?.\)", "", item_string)

        l = []
        l.extend(parse_item_list(item_string))
        if not self.compare_lists(self.list, l):
            #magentaprint("Inventory.set_inventory OVERWRITING self.list with %s." % str(l))
            self.list = l
            # Referencing list implements nice counted dict output for self.to_string
            magentaprint("Inventory.set_inventory that is {0}".format(self))
            self.sellable_assuming_correctness()
            #magentaprint(self) # Could try cyan print
        else:
            magentaprint("Inventory.set_inventory didn't overwrite self.list, lengths: %s, %s." % (len(l), len(self.list)))
            self.sellable_assuming_correctness()

    def compare_lists(self, l1, l2):
        if len(l1) != len(l2):
            return False

        for i in range(0, len(l1)):
            if l1[i] != l2[i]:
                return False

        return True

    def compare_mud_object_dicts(self, d1, d2):
        # This won't check is_usuable as desired
        # We just care that all item names match and the quantities match,
        # since that is all of the info provided by the inventory command

        # if len(d1.keys()) != len(d2.keys()) or len(d1.values()) != len(d2.values()):
        if len(d1.dictionary.keys()) != len(d2.dictionary.keys()):
            return False

        for k in d1.dictionary.keys():
            if k in d2.dictionary.keys():
                if len(d1.dictionary[k].objs) != len(d2.dictionary[k].objs):
                    return False
            else:
                return False

        # This could miss some wonky differences
        return True

    # def add(self, item_string):
    #     self.inventory.add(parse_item_list_dict(item_string))

    # def add_broken(self, item_string):
    #     # Hmph - this would be the simple way to do it...
    #     items = parse_item_list_dict(item_string)

    #     for item in items:
    #         item.is_unusable = True

    #     self.inventory.add(items)

    # def mark_broken(self, item_ref):
    #     # if len(item_ref.partition(' ')) >= 2:
    #     #     self.inventory.inventory[item_ref.partition(' ')[0]].objs[int(item_ref.partition(' '))].is_unusable = True
    #     # else:
    #     #     self.inventory.inventory[item_ref.partition(' ')[0]].objs[0].is_unusable = True
    #     # self.get(item_ref).objs
    #     self.set_unusable(item_ref)
    # def set_broken(self, item_ref):
    #     self.mark_broken(item_ref)

    def remove_many(self, item_string):
        item_list = parse_item_names(item_string)

        for s in item_list:
            # magentaprint("Inventory.remove_many() calling remove_by_ref on " + str(self.get_reference(s)))
            ref = self.get_reference(s)
            if ref:  # Happens if inv is not up to date (ie. Bought.)
                self.remove_by_ref(ref)

    def equip_item(self, equip_string):
        self.telnetHandler.write(equip_string)
        self.wait_for_flag()

    def sellable(self):
        # TrackGrind is calling this every even track
        self.get_inventory() # This line isn't necessary if we assume everything is always works perfectly
        return self.sellable_assuming_correctness()
    def sellable_assuming_correctness(self):
        slist = self.get_unique_references(self.keep_list)
        slist.reverse()
        magentaprint("Sellable items: " + str(slist)) # This is a good print that shows ie. ['the', 'sabre']
        # magentaprint("Sellable items: " + str(ReferencingList([self.get(i) for i in slist if self.get(i) is not None]))) 
        magentaprint("Sellable items: " + str(ReferencingList([self.get(i) for i in slist if self.get(i) != None]))) 
        # Ok program that defensively (if not None)
        magentaprint("Keeping items: " + str(ReferencingList(
            [i for i in self.list if i in self.keep_list and i != None])))
        self.telnetHandler.write('')
        # Can't make a referencing list with None, right...
        # return self.inventory.get_unique_references(self.keep_list)
        return slist
        #https://www.geeksforgeeks.org/python-intersection-two-lists/

    def droppable(self):
        # Maybe don't refesh the inventoy at this point
        # Because we don't know what can sell at the pawn shop
        # And we don't know what we picked up?
        # Hmmm... we need to make a drop list at the pawn shop
        # Ok this uses item.usable...
        # I think that the bot drops everything "sellable" when it's at the tip
        # Quotes on "sellable" meaning, we already tried to sell it to the pawn shop guy and he didn't buy it.
        return self.broken_junk()

    def broken_junk(self):
        refs = []
        # unique_refs = self.get_unique_references(self.list)
        # for uref in unique_refs:
        for item in self.list:
            item_name_split = item.name.split(' ')
            if len(item_name_split) > 1:
                # magentaprint("broken junk %s unusable: %s" % (item, str(item.is_unusable)))
                if item_name_split[1] == 'ring' and not item.usable:
                    # magentaprint("broken_junk appending " + str(self.get_reference(item)))
                    refs.append(self.get_reference(item))
                    # first_ref = self.get_reference(item)
                    # if len(first_ref.split(' ')) > 1:
                    #     refs.append(first_ref.split(' ')[0] + ' ' + str(int(first_ref.split(' ')[1]) + index))
                    # else:
                    #     if index > 0:
                    #         # refs.append(first_ref.split(' ')[0] + ' ' + str(index + 1))
                    #         refs.append(first_ref + ' ' + str(index + 1))
                    #     else:
                    #         refs.append(first_ref)
                # elif item_name == 'small inhaler' and not qty.objs[index].is_usable::
                # drop_item_at_index(item, index)  # This would require a get_reference_from_index method

        refs.reverse() # Caller assumes it can use all the references in order (this reverse is needed)
        magentaprint("broken junk returning " + str(refs))
        return refs  # Bot can drop these references without reversing
        # TODO: use small inhalers

    def broken_junk_dict(self):
        # self.get_inventory()
        # for item_list in self.inventory.dictionary.values():
        #     magentaprint("Inventory droppable item list: " + str(self.inventory.dictionary.values()))

        refs = []
        for item,qty in self.inventory.dictionary.items():
            for index, gobj in enumerate(qty.objs):
                item_name_split = qty.objs[index].obj.name.split(' ')
                if len(item_name_split) > 1:
                    magentaprint("broken junk %s usable: %s" % (qty.objs[index].obj.name, str(qty.objs[index].usable)))
                    if item_name_split[1] == 'ring' and not qty.objs[index].usable:
                        # Build a reference from an index... maybe this could be a separate method for future use
                        first_ref = self.get_reference(qty.objs[index].to_string())  # Hopefully the item order is legit...
                        # first_ref = self.get_reference(str(gobj))
                        if len(first_ref.split(' ')) > 1:
                            refs.append(first_ref.split(' ')[0] + ' ' + str(int(first_ref.split(' ')[1]) + index))
                        else:
                            if index > 0:
                                # refs.append(first_ref.split(' ')[0] + ' ' + str(index + 1))
                                refs.append(first_ref + ' ' + str(index + 1))
                            else:
                                refs.append(first_ref)
                    # elif item_name == 'small inhaler' and not qty.objs[index].is_usable::
                    # drop_item_at_index(item, index)  # This would require a get_reference_from_index method

        refs.reverse()
        magentaprint("broken junk returning " + str(refs))
        return refs  # Bot can drop these references without reversing
        # TODO: use small inhalers

    def output_inventory(self):
        magentaprint(str(self.list), False)

    # usable = ["small retorative", "large restorative", "chicken soup", "scarlet potion",
    #           "steel bottle", "silver chalice", "milky potion",
    #           "glowing potion",
    #           "adamantine rod", "granite rod", "zinc wand"]

    # should probably depend on level.
    #keep_list = ["small restorative", "silver chalice", "steel bottle", "milky potion"]
    #thick liquid silences you !!!  (mimes are funny)

    MUD_RETURN_ITEM_SOLD = False

    def list_form(self):
        # Assuming {item_name: qty} string:int structure
        l = []
        for k in self.inventory.dictionary.keys():
            l.extend([k] * len(self.inventory.dictionary[k].objs))
        return l

    # def get_reference(self, item_name, first_or_second_word=1):
    #     return self.list.get_reference(item_name, first_or_second_word)

    #     item_words = item_name.strip().split(' ')
    #     # self.inventory.sort()  # I think we can assume that proper housekeeping has been done
    #     # This would be easier with a simple list than with the qty dict
    #     # Algorithm: Use the first word in the item.  Count the items in the inventory that also
    #     # use that word.  Return a word/int pair that will serve as a usable reference (ie. 'steel 6')
    #     i = 1
    #     word = item_words[0] if first_or_second_word == 1 or len(item_words) <= 1 else item_words[1]
    #     for k in sorted(self.inventory.dictionary.keys()):  # TODO: We can probably save time here
    #         if word in k.obj.name.split(' '):
    #             if item_name == k.obj.name:
    #                 return word if i == 1 else word + ' ' + str(i)
    #             else:
    #                 i = i + len(self.inventory.dictionary[k].objs)

    #     return None  # Not in inventory - would be easy to check for that before calling

    # def get_2nd_word_reference(self, item_name):
    #     return self.get_reference(item_name, 2)

    # def get_last_reference(self, item_name, first_or_second_word=1):
    #     # Often you want the most recent item in the stack
    #     starting_point = self.get_reference(item_name, first_or_second_word)
    #     if starting_point is None:
    #         return None
    #     c = self.count(item_name)
    #     magentaprint("Inv get_last_reference counted " + str(c))
    #     ref_split = starting_point.split(' ')
    #     if len(ref_split) > 1:
    #         return starting_point.split(' ')[0] + ' ' + str(int(ref_split[1]) + c - 1)
    #     else:
    #         if c <= 1:
    #             return starting_point.split(' ')[0]  # Had a buggy c as 0 case - and the served targets odd things with n=0
    #         else:
    #             return starting_point.split(' ')[0] + ' ' + str(c)
    #     # There would be less code if I didn't treat '1' specially (I prefer 'potion' not 'potion 1' for the 1st potion)

    # def _reference_string(self, word, i):
    #     # Reference string given the int - this is just a code-saving method
    #     if i <= 1:
    #         return word
    #     else:
    #         return word + ' ' + str(i)

    def remove_a_an_some(self, item_string):
        if item_string.startswith('A '):
            return item_string[2:]
        elif item_string.startswith('An '):
            return item_string[3:]
        elif item_string.startswith('Some '):
            return item_string[5:]
        else:
            return item_string

    def item_from_reference(self, ref):
        return self.get(ref)
    #     ref_split = ref.split(' ')
    #     ref_string = ref_split[0]

    #     if len(ref_split) > 1:
    #         ref_n = int(ref_split[1])
    #     else:
    #         ref_n = 1

    #     # ilist = sorted(self.inventory.keys())
    #     for itemkey, ivalue in self.inventory.dictionary.items():  # Hopefully sorted by keys...
    #         if any([w.startswith(ref_string) for w in itemkey.to_string().split(' ')]):
    #             if ref_n < ivalue.qty:
    #                 return ivalue.objs[ref_n-1]
    #             ref_n = ref_n - ivalue.qty

    def name_from_reference(self, ref):
        return str(self.item_from_reference(ref))

    def get_item_name_from_reference(self, ref):
        # # A list would be better
        # ref_split = ref.split(' ')
        # ref_string = ref_split[0]

        # if len(ref_split) > 1:
        #     ref_n = int(ref_split[1])
        # else:
        #     ref_n = 1

        # # ilist = sorted(self.inventory.keys())
        # for itemkey, ivalue in self.inventory.dictionary.items():  # Hopefully sorted by keys...
        #     if any([w.startswith(ref_string) for w in itemkey.to_string().split(' ')]):
        #         if ref_n <= ivalue.qty:
        #             return itemkey.to_string()
        #         ref_n = ref_n - ivalue.qty

        return self.get_item_from_reference(ref).to_string() if self.get_item_from_reference(ref) else None

    def get_item_from_reference(self, ref):
        return self.get(ref)
        # # !!! Needs improvement!  Use get_item_name_from_reference
        # word, n = ref.partition(' ')[0], int(ref.partition(' ')[2])
        # # Go through ordered keys, counting down, to determine the targeted item
        # for item in self.inventory.dictionary.keys():
        #     if any([w.startswith(word) for w in item.to_string().split(' ')]):
        #         if n <= self.inventory.dictionary[item].qty:
        #             return self.inventory.dictionary[item]
        #         else:
        #             n = n - self.inventor

        # Copying code exactly from get_item_name_from_reference
        ref_split = ref.split(' ')
        ref_string = ref_split[0]

        if len(ref_split) > 1:
            ref_n = int(ref_split[1])
        else:
            ref_n = 1

        for itemkey, ivalue in self.inventory.dictionary.items():  # Hopefully sorted by keys...
            if any([w.startswith(ref_string) for w in itemkey.to_string().split(' ')]):
                if ref_n <= ivalue.qty:
                    return ivalue.objs[ref_n-1]
                ref_n = ref_n - ivalue.qty  # This "overloads" ref_n a bit, counting it down as we loop

    def unequip_weapon(self, weapon):
        # e = self.equipped_items
        # if 'Wielded' in e.keys():
        #     if 'Second' in e.keys() and e['Wielded'] == e['Second'] and e['Wielded'] == weapon:
        #         # Unknown which broke: guess and don't rely on it
        #         del e['Wielded']  # can't del with just 'e'
        #     elif e['Wielded'] == weapon:
        #         del e['Wielded']
        # if 'Second' in e.keys() and e['Second'] == weapon:
        #     del e['Second']

        magentaprint('Inventory.unequip_weapon() ' + str(self.equipped_items.keys()))
        if 'Wielded' in self.equipped_items.keys() and self.equipped_items['Wielded'] and self.equipped_items['Wielded'][0].obj.name == weapon:
            # Could be wrong if the second weapon is the same and that broke
            magentaprint('Inventory.unequip_weapon() deleting Wielded (' + str(self.equipped_items['Wielded']) + ')')
            del self.equipped_items['Wielded']
            magentaprint(str(self.equipped_items))
        elif 'Second' in self.equipped_items.keys() and self.equipped_items['Second'] and self.equipped_items['Second'][0].obj.name == weapon:
            del self.equipped_items['Second']

    def count(self, item_string):
        mud_item = MudItem(item_string)
        mud_item.map()
        return self.list.count(mud_item)

    def first_usable_ring_ref(self):
        count = 0
        for item in self.list:
            if 'ring' in str(item).split():
                count = count + 1
            if len(str(item).split()) == 2 and str(item).split()[1] == 'ring':
                if item.usable:
                    if count > 1:
                        return 'ring ' + str(count)
                    else:
                        return 'ring'

# Ok I want to set up reactions to keep myself up to date.
# I am thinking of steel bottles and restoratives, so I want
# a function to return how many I have.
# How about losHelper sets me up.  I think that's doable.

# Ok what about selling, dropping, giving, wielding, wearing.
# I think I can see why I never wrote this thing.
# Well how about we just make it stupid a ignore those things.
# (Alternative is to ask command_handler to do all of these things
# through the inventory object... inventory.sell() inventory.wear()
# which isn't terrible.  Hmmmm)

# The obvious case is picking up, so we should have a reaction for that.
# (I think BotReactions needs to have a regex list...!)  Makes it a bit
# harder to use, since you need to put in a list.  Well can we make the
# list optional?  That isn't much better.

# Ok I am ready for a regex list in BotReactions.

# Plan is to have a Sel object that supports a non-blocking and blocking call
# It can store the command that was sent to get the right item removed from inventory
# This applies to a lot of other things - drop, give, wear
# Stores the command(s) that went out
# Not sure if each command needs its own class

# The plan now is to have a sell object, and have it remember the command that was sent.
# That way it can correct the inventory in notify()
# Which means calls to Sell don't have to be blocking
# So I think that Sell will "have" inventory.
# Inventory "having" sell... well, sell would also need to "have" inventory.
# So why not just put inventory at the bottom.
# Then it doesn't need to watch the sell regexes.
# (Inventory is a command that still has to deal with executing and waiting for "you_have")

# BUYING STUFF

# Hmmm, how to keep inventory up to date when buying stuff?
# How about printing the inventory on this regex?
# Oooh, maybe we could convince MudReaderThread to repress the output.
# Well, we could have command_handler call 'buy' and then confirm ...
# oooff that doesn't even work because we don't have the full name of what we bought
# (Database should know that)
# Maybe printing the inventory won't be too annoying...

# NEWLINES

# I wonder if there's a bug whenever a newline occurs outside of the (.+?).
# That would probably be MudReader's job to fix on a global level.
# No, the mud doesn't put newlines there.  The console will wrap it but
# that doesn't constitute a newline.  The mud always puts them between words.
# so s = s.replace('\r\n', ' ') is always a good move.

# Would be nice to keep track of white amulet usages, also small flask
# It'd be good to consider the weight when deciding whether to sell.

# Your brass ring fell apart.
# You are not yet adept enough to use this!
