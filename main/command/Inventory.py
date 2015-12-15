
import time, re, collections

from Exceptions import *
from reactions.BotReactions import *
from misc_functions import *
from db.MudItem import *
from reactions.referencing_list import ReferencingList
import comm.RegexStore as R

class Inventory(BotReactionWithFlag, ReferencingList):
    # keep_list = ["large bag", "large sack", "black bag",
    #     "silver chalice", "steel bottle", 'glowing potion',
    #     "chicken soup", 'scarlet potion', 'white potion', "tree root",
    #     "Elixir of Morinva", "granite potion", "philtre of perception",
    #     "burnt ochre potion", "milky potion"]

    keep_list = [
        'large bag', 'large sack', 'black bag','silver chalice', 'steel bottle', 'glowing potion', 'milky potion',
        'chicken soup', 'small restorative', 'small flask', 'large restorative', 'scarlet potion', 'white potion', 'tree root', 
        'Elixir of Morinva', 'granite potion', 'philtre of perception', 'burnt ochre potion', 'granite rod', 'heathen amulet',
        # 'spear', 
        # 'bolos', 
        'javelin', 'heavy crossbow', 
        #'crossbow', 'horn bow', 'long bow' # < 70% missile
        # 'broad sword', 
        'adamantine axe', 'rapier', 'adamantine sword', 'claymore', 'spider leg', 'large orcish sword', 
        # 'silver dagger',
        # 'long sword',  these pile up
        #'bastard sword',  # bandits
        'small mace', 'morning star'
        # 'war hammer', 
        'hard cap', 'hard gloves', 'hard boots', 'padded hat', 'mountain gloves', 'mountain boots', 
        'mountain boots with crampons', 'travellers cross', 'leather mask', 'leather collar', 'studded leather collar', 
        'studded leather sleeves', 'studded leather boots', 'studded leather pants', 'studded leather gloves', 
        'studded leather leggings' 'plate mail leggings', 'plate mail armor',
        'ring mail armour', 'ring mail sleeves', 'ring mail leggings', 'ring mail hood', 
        # 'ring mail gauntlets', 
        # 'chain mail armour',  # sawmill
        'chain mail sleeves', 'chain mail leggings', 'chain mail hood', 'chain mail boots', 
        # 'chain mail gloves', # mill worker
        'enchanted indigo cloak', 'fine elven cloak', 'light elven cloak', 'lion charm', 'poison ring',
        'iron shield', 'platinum ring', 'gold ring', 'steel ring', 'silver ring',
        #'steel mask' # spiv, sawmill
    ]

    def __init__(self, telnetHandler, character):
        self.regex_cart = [
            R.you_have, R.wont_buy, R.wont_buy2, R.sold, R.you_drop, R.disintegrates, R.gold_from_tip, R.not_a_pawn_shop, 
            R.you_now_have, R.not_empty, R.you_wear, R.nothing_to_wear, R.you_get, R.you_remove, R.nothing_to_remove, R.you_wield, 
            R.you_give, R.bought, R.you_put_in_bag, R.gave_you, R.you_hold, R.weapon_break, R.weapon_shatters, R.armor_breaks, 
            R.current_equipment, R.no_inventory, R.wearing
        ]
        self.telnetHandler = telnetHandler
        self.character = character
        self.gold = 0
        self.__stopping = False
        self.is_bulk_vendoring = False
        self.equipped_items = {}
        # equipped_items = {'body': [], 'arms':[], 'legs':[],'neck':[],'hands':[],'head':[],'feet':[],'face':[],'finger':[],'Shield':[],'Wielded':[],'Second':[]}

        for index, item in enumerate(self.keep_list):
            self.keep_list[index] = MudItem(item)

        self.restoratives = [
            'chicken soup', 'small restorative', 'small flask', 'large restorative', 'scarlet potion', 'white potion'
        ] # , 'tree root']

        BotReactionWithFlag.__init__(self)
        ReferencingList.__init__(self)

    def notify(self, regex, M_obj):
        if regex in R.you_have:
            # magentaprint('Inventory you_have item list: ' + M_obj.group(1))
            self.set_inventory(M_obj.group(1))
            # magentaprint(str(self.list))
        elif regex in R.sold:
            self.gold = self.gold + int(M_obj.group(1))
            self.remove_many(M_obj.group(2))
        elif regex in R.you_now_have + R.gold_from_tip:
            self.gold = int(M_obj.group(1))
        elif regex in R.you_wield and not M_obj.group('weapon').endswith('in your off hand'):
            weapon = M_obj.group('weapon')
            self.equipped_items['Wielded'] = [MudItem(weapon)]
            magentaprint('Just made object ' + str(self.equipped_items['Wielded'][0].obj.name))
            self.remove_many(weapon)
            # self.get_equipment()
        elif regex in R.off_hand:
            self.equipped_items['Second'] = [MudItem(weapon)]
            self.remove_many(weapon)
            # self.get_equipment()
        elif regex in R.you_get:
            item = self.clip_from_a_container(M_obj.group(1))
            self.add(item)
        elif regex in R.you_drop + R.you_give + R.you_put_in_bag + R.disintegrates:
            # magentaprint(str(M_obj.group(1)), False)
            # Problem: we don't know which item was dropped, so it's hard to keep track of is_usable
            # Maybe we just want to reset everthing after dropping... or the bot needs to manage things,
            # or inventory needs full control of many commands (drop, sell...) ... hmph ... preferring to 
            # ask the server
            self.remove_many(M_obj.group(1))
        elif regex in R.you_wear + R.you_hold:
            self.remove_many(M_obj.group(1))
            self.get_equipment()
            #we know this is armor of some kind so we need to find a way to assign it to the right spot
        elif regex in R.you_remove + R.gave_you:
            self.add(M_obj.group(1))
        elif regex in R.bought:
            pass
            # if not self.is_bulk_vendoring:
            #     self.get_inventory()  # There are some notes about this at the bottom
            #     # I don't like this very much! I can't use ! to buy a lot of a thing.
        elif regex in R.weapon_break + R.armor_breaks:
            magentaprint('Inventory weapon / armor break')
            item = M_obj.group(1)
            self.add_broken(M_obj.group(1)) 
            # self.get_equipment()
            self.unequip_weapon(item)
        elif regex in R.weapon_shatters:
            magentaprint('Inventory weapon_shatters')
            item = M_obj.group(1)
            self.unequip_weapon(item)
        elif regex in R.current_equipment:
            character_name = M_obj.group(1)  # TODO: This works for 'l self' but not for 'eq'
            equipment_list = re.findall(R.wearing[0], M_obj.group(2))

            if character_name == self.character.name:
                for slot in equipment_list:
                    if slot[0] not in self.equipped_items:
                        self.equipped_items[slot[0]] = []

                    self.equipped_items[slot[0]].append(MudItem(slot[1]))
            # magentaprint(self.equipped_items,False)
        # magentaprint(self.list, False)
        super().notify(regex, M_obj)

    def get_inventory(self):
        # magentaprint('\n' + str(self.list))
        self.telnetHandler.write('i')
        self.wait_for_flag()
        # magentaprint('\n' + str(self.list))
        return self.list

    def get_equipment(self):
        return
        # self.telnetHandler.write("l ' + self.character.name)
        # self.wait_for_flag()

    # def has(self, mud_item_string):
    #     mud_item = MudItem(mud_item_string)
    #     mud_item.map()

    #     if self.inventory.count(mud_item) > 0:
    #         return True

    #     return False

    def has_restorative(self):
        return any([self.has(r) for r in self.restoratives])

    def count_restoratives(self):
        return sum(self.count(r) for r in self.restoratives)

    def has_any(self, item_name_list):
        return any([self.has(i) for i in item_name_list])  

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

    def get_item_of_type(self, item_model, item_data, level=1):
    #     return self.inventory.get_object_of_type(itemModel, itemData, level)
        return self.get_object_of_type(item_model, item_data, level)

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
        self.telnetHandler.write("sell " + item_ref)
        self.wait_for_flag()

    def bulk_sell(self, item_string, quantity):
        i = 0
        magentaprint("Bulk selling: " + item_string + " #" + quantity)
        self.is_bulk_vendoring = True

        while i < (quantity ):
            self.sell(item_string)
            i += 1

        time.sleep(3) #breathe!

        self.is_bulk_vendoring = False

    def buy_stuff(self, item_string):
        #this should be implemented to match sell stuff
        #programmatic purchasing via a shopping list or something
        return

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

    # def sell_fast(self):

    def drop_stuff(self):
        magentaprint("Inventory.drop_stuff()")
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
        self.telnetHandler.write("drop " + item_ref)
        self.wait_for_flag()

    def drop_last(self, item_string):
        # item_ref = self._item_string_to_reference(item_string)  # TODO: This looks like it would crash
        item_ref = self.get_last_reference(item_string)
        self.telnetHandler.write("drop " + item_string  + " " + str(position))
        self.wait_for_flag()

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
        magentaprint("Inventory.add %s parsed as %s." % (item_string, str(self.parse_item_list(item_string))))

        items = self.parse_item_list(item_string)  # This is overloaded for "hammer" and "a hammer"
        for i in items:
            # magentaprint("Inventory adding %s" % str(i))
            super().add(i)

    def add_broken(self, item_string):
        items = self.parse_item_list(item_string)

        for i in items:
            i.is_unusable = True
            super().add(i)

    def add_broken_to_dict(self, item_string):
        # items = self.parse_item_list(item_string)

        # for name, qty in items:
        #     for i in range(0,qty):
        #         item = MudItem(name)
        #         item.is_unusable = True
        #         self.add(item)
        # for name in item_string: # separates out letters...
        for itemkey, itemlist in self.parse_item_list_dict(item_string).items():
            for item in itemlist:
                self.add(item.to_string())
                magentaprint("Inv add broken on ref " + self.get_last_reference(item.to_string()))
                self.set_broken(self.get_last_reference(item.to_string()))
                # This is something crazy like O(n^4) but I'm having a hard time... 
                # so I'm avoiding constructing MudItem, GenericMudList, MudObjectDict in order to avoid adding to 
                # MudObjectDict one at a time.  Its add function requires another dict as input.

    def set_broken(self, ref):
        self.get_item_from_reference(ref).is_unusable = True

    def set_inventory(self, item_string):  
        # self.inventory = MudObjectDict()
        # self.inventory.add(self.parse_item_list_dict(item_string))
        # self.inventory = MudObjectDict().add(self.parse_item_list_dict(item_string))  # constructor doesn't return self

        # d = MudObjectDict()
        # d.add(self.parse_item_list_dict(item_string))
        # # This overwrites all state information (is_unusable), so only overwrite when the new dict is somehow different.
        # if not self.compare_mud_object_dicts(d, self.inventory):
        #     self.inventory = d

        l = []
        l.extend(self.parse_item_list(item_string))
        if not self.compare_lists(self.list, l):
            magentaprint("Inventory.set_inventory overwriting self.list, len %s." % len(l))
            magentaprint(str(self.to_dict()))
            self.list = l
        else:
            magentaprint("Inventory.set_inventory didn't overwrite self.list, lengths: %s, %s." % (len(l), len(self.list)))

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
    #     self.inventory.add(self.parse_item_list_dict(item_string))

    # def add_broken(self, item_string):
    #     # Hmph - this would be the simple way to do it...
    #     items = self.parse_item_list_dict(item_string)

    #     for item in items:
    #         item.is_unusable = True

    #     self.inventory.add(items)

    def mark_broken(self, item_ref):
        # Untested
        if len(item_ref.partition(' ')) >= 2:
            self.inventory.inventory[item_ref.partition(' ')[0]].objs[int(item_ref.partition(' '))].is_unusable = True
        else:
            self.inventory.inventory[item_ref.partition(' ')[0]].objs[0].is_unusable = True

    def remove_many(self, item_string):
        item_list = self.parse_item_names(item_string)

        for s in item_list:
            magentaprint("Inventory.remove_many() calling remove on " + str(self.get_reference(s)))
            if self.get_reference(s) is not None:  # Happens if inv is not up to date (ie. Bought.)
                self.remove(self.get_reference(s))

    def equip_item(self, equip_string):
        self.telnetHandler.write(equip_string)
        self.wait_for_flag()

    def clip_in_your_off_hand(self, wield_string):
        # Example wield_string: a spear in your off hand
        wield_string = wield_string.replace('\n\r', ' ')
        length = len(wield_string)

        if wield_string[length-17:length] == " in your off hand":
            return wield_string[:length-17]
        else:

            return wield_string

    def clip_from_a_container(self, get_string):
        # Example get_string: some chicken soup from a sack
        get_string = get_string.replace('\n\r', ' ')
        M_obj = re.search("(.+?) from (.+?)", get_string)

        if M_obj != None:
            return M_obj.group(1)
        else:
            return get_string

    def construct_items(self, string_list):
        items = []

        for i in string_list:
            item = MudItem(i)
            item.map()
            items.append(item)

        return items

    def parse_item_list(self, inventory_string):
        return self.construct_items(self.parse_item_names(inventory_string))

    def parse_item_names(self, inventory_string):
        # returns a list of strings (MudItems can be constructed outside)

        return_list = []
        inventory_string = inventory_string.replace("\n\r", ' ')
        inv_list = inventory_string.split(',')
        inv_list = [item.strip(' \t\n\r') for item in inv_list]
        singles = ['a ', 'an ', 'some ']
        numbers = ['two ', 'three ', 'four ', 'five ', 'six ', 'seven ', 
                   'eight ', 'nine ', 'ten ', 'eleven ', 'twelve ', 'thirteen ', 'fourteen ', 
                   'fifteen ' , 'sixteen ', 'seventeen ', 'eighteen ', 'nineteen ', 'twenty '] 
        numbers.extend([str(i) + " " for i in range(21, 200)])

        for item in inv_list:
            if item.endswith(" gold coin") or item.endswith(" gold coins"):
                continue
            if item.endswith(" platinum coins"):
                continue

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

                    if item.endswith('ses') or item.endswith('xes'):
                        item = item[:len(item)-2]
                    elif item.endswith('s'):
                        item = item[:len(item)-1]

                    return_list.extend([item]*(n+2))

        return return_list

    def parse_item_list_dict(self, inventory_string):
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
            gold_coin_match = re.match("(\d+) gold coins?", item)
            if gold_coin_match:
                # self.add_to_dict(return_dict, 'gold coin', int(gold_coin_match.group(1)))
                continue
            for s in singles:
                if item[0:len(s)] == s:
                    number_found = True
                    self.add_to_dict(return_dict, item[len(s):], 1)
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
                    self.add_to_dict(return_dict, item, n+2)
                    break
            if number_found is False:
                magentaprint("Inventory parsed " + item)
                #if the item wasn't received with a/an/some etc...
                #we assume it's just one item
                # mud_item = MudItem(item)
                # mud_item.map()
                # item_list = GenericMudList([mud_item])
                # return_dict[mud_item] = item_list
                self.add_to_dict(return_dict, item, 1)

        return return_dict

    def add_to_dict(self, d, item_str, qty):
        mud_item = MudItem(item_str)
        mud_item.map()
        d[mud_item] = GenericMudList([mud_item] * qty)

    def sellable(self):
        self.get_inventory()
        slist = self.get_unique_references(self.keep_list)
        slist.reverse()
        magentaprint("Sellable items: " + str(slist))
        # return self.inventory.get_unique_references(self.keep_list)
        return slist

    def droppable(self):
        return self.broken_junk()

    def broken_junk(self):
        refs = []
        # unique_refs = self.get_unique_references(self.list)
        # for uref in unique_refs:
        for item in self.list:
            item_name_split = item.name.split(' ')
            if len(item_name_split) > 1:
                magentaprint("broken junk %s unusable: %s" % (item, str(item.is_unusable)))
                if item_name_split[1] == 'ring' and item.is_unusable:
                    magentaprint("broken_junk appending " + str(self.get_reference(item)))
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

        refs.reverse()
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
                    magentaprint("broken junk %s unusable: %s" % (qty.objs[index].obj.name, str(qty.objs[index].is_unusable)))
                    if item_name_split[1] == 'ring' and qty.objs[index].is_unusable:
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
            magentaprint('Inventory.unequip_weapon() deleting Wielded')
            del self.equipped_items['Wielded']
            magentaprint(str(self.equipped_items))
        elif 'Second' in self.equipped_items.keys() and self.equipped_items['Second'] and self.equipped_items['Second'][0].obj.name == weapon:
            del self.equipped_items['Second']

    def count(self, item_string):
        mud_item = MudItem(item_string)
        mud_item.map()
        return self.list.count(mud_item)

# Ok I want to set up reactions to keep myself up to date.
# I am thinking of steel bottles and restoratives, so I want 
# a function to return how many I have.
# How about losHelper sets me up.  I think that's doable.

# Ok what about selling, dropping, giving, wielding, wearing.  
# I think I can see why I never wrote this thing.  
# Well how about we just make it stupid a ignore those things.
# (Alternative is to ask commandHandler to do all of these things
# through the inventory object... inventory.sell() inventory.wear()
# which isn't terrible.  Hmmmm)

# The obvious case is picking up, so we should have a reaction for that.
# (I think BotReactions needs to have a regex list...!)  Makes it a bit 
# harder to use, since you need to put in a list.  Well can we make the 
# list optional?  That isn't much better.

# Ok I am ready for a regex list in BotReactions.

# Your brass ring fell apart.
# You are not yet adept enough to use this!


# BUYING STUFF

# Hmmm, how to keep inventory up to date when buying stuff?
# How about printing the inventory on this regex? 
# Oooh, maybe we could convince MudReaderThread to repress the output.
# Well, we could have commandHandler call 'buy' and then confirm ... 
# oooff that doesn't even work because we don't have the full name of what we bought
# Maybe printing the inventory won't be too annoying... 

# NEWLINES

# I wonder if there's a bug whenever a newline occurs outside of the (.+?).  
# That would probably be MudReader's job to fix on a global level.
# No, the mud doesn't put newlines there.  The console will wrap it but 
# that doesn't constitute a newline.  The mud always puts them between words.
# so s = s.replace('\r\n', ' ') is always a good move.

# Would be nice to keep track of white amulet usages
# It'd be good to consider the weight when deciding whether to sell.
