
import time
import re

from Exceptions import *
from BotReactions import *
from misc_functions import *


class Inventory(BotReactionWithFlag):

    def __init__(self, mudReaderHandler, telnetHandler):
        self.you_have = "(?s)You have: (.+?)\."
        self.wont_buy = "The shopkeep says, \"I won't buy that rubbish from you\.\""
        self.wont_buy2 = "The shopkeep won't buy that from you\."
        self.sold = "The shopkeep gives you (.+?) gold for (.+?)\."
        self.you_drop = "(?s)You drop (.+?)\."
        self.gold_from_tip = "You have (.+?) gold\."
        self.not_a_pawn_shop = "This is not a pawn shoppe\."
        self.you_now_have = "You now have (.+?) gold pieces\."
        self.not_empty = "It isn't empty!"
        self.you_wear= "(?s)You wear (.+?)\."
        self.nothing_to_wear = "You have nothing you can wear\."
        self.you_get = "(?s)You get (.+?)\."
        self.you_remove = "(?s)You removed? (.+?)\."
        self.nothing_to_remove = "You aren't wearing anything that can be removed\."
        self.you_wield = "You wield (.+?)\."
        self.you_give = "(?s)You give (.+?) to (.+?)\."
        self.bought = "Bought\."  
        self.you_put_in_bag = "(?s)You put (.+?) in(to)? (.+?)\."
        self.gave_you = ".+? gave (.+?) to you\."

        self.regexes = [self.you_have, self.you_get, self.wont_buy, self.wont_buy2, self.sold, 
            self.you_drop, self.not_a_pawn_shop, self.you_now_have, self.gold_from_tip,
            self.not_empty, self.you_wear, self.nothing_to_wear, self.you_remove,  
            self.nothing_to_remove, self.you_wield, self.you_give, self.bought,
            self.you_put_in_bag, self.gave_you]

        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.inventory = []
        self.gold = 0
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex is self.you_have:
            self.set_inventory(M_obj.group(1))
        elif regex is self.sold:
            self.gold = self.gold + int(M_obj.group(1))
            self.remove(M_obj.group(2))
        elif regex is self.you_now_have or regex is self.gold_from_tip:
            self.gold = int(M_obj.group(1))
        elif regex is self.you_wield:
            weapon = self.clip_in_your_off_hand(M_obj.group(1))
            self.remove(weapon)
        elif regex is self.you_get:
            item = self.clip_from_a_container(M_obj.group(1))
            self.add(item)
        elif regex is self.you_drop or regex is self.you_wear or regex is self.you_give or regex is self.you_put_in_bag:
            self.remove(M_obj.group(1))
        elif regex is self.you_remove or regex is self.gave_you:
            self.add(M_obj.group(1))
        elif regex is self.bought:
            self.get_inventory()  # There are some notes about this at the bottom
            # I don't like this very much! I can't use ! to buy a lot of a thing.

        super(Inventory, self).notify(regex, M_obj)  # sets __waiter_flag

    def get_inventory(self):
        self.telnetHandler.write("i")
        self.wait_for_flag()
        return self.inventory

    def has_restorative(self):
        return self.has(self.restoratives)

    def use_restorative(self):
        self.use(self.restoratives)

    def has(self, item_or_list):
        if type(item) is list:
            return any([i in self.inventory for i in item])
        else:
            return item_or_list in self.inventory

    def use(self, item_or_list):
        item = ""
        if type(item) is list:
            for i in item_or_list:
                if i in self.inventory:
                    item = i
                    break
        else:
            item = item_or_list

        self.telnetHandler.write("use " + item)
        Inventory.remove_from_qty_dict(self.inventory, (item, 1))
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
        self.get_inventory()  # Unnecessary if inventory is well tracked

        for item_ref in self.sellable():
            if not self.__stopping:
                self.sell(item_ref)
            else:
                return

    def sell(self, item_ref):
        self.telnetHandler.write("sell " + item_ref)
        self.wait_for_flag()

    # def sell_fast(self):

    def drop_stuff(self):
        self.__stopping = False
        self.get_inventory()  # Maybe unnecessary, except I see "You don't have that" if removed

        for item_ref in self.sellable():
            if not self.__stopping:
                self.drop(item_ref)
            else:
                return

    def drop(self, item_ref):
        self.telnetHandler.write("drop " + item_ref)
        self.wait_for_flag()

    def stop(self):
        self.__stopping = True

    def set_inventory(self, item_string):
        self.inventory = self.parse_item_list(item_string)

    def add(self, item_string):
        items = self.parse_item_list(item_string)

        for item, qty in items.items():
            if item != 'gold coin':
                Inventory.add_to_qty_dict(self.inventory, (item, qty)) 

    @staticmethod
    def add_to_qty_dict(d, duple):
        ''' For (key, qty) pairs. '''
        if duple[0] in d:
            d[duple[0]] += duple[1]
        else:
            d[duple[0]] = duple[1]

    def remove(self, item_string):
        items = self.parse_item_list(item_string)

        for item, qty in items.items():
            if item != 'gold coin':
                try:
                    # self.remove((item, qty))
                    Inventory.remove_from_qty_dict(self.inventory, (item, qty))
                except ValueError:
                    magentaprint("Couldn't remove '" + item + "' from inventory.")
                    magentaprint("inventory:" + str(self.inventory))
                    magentaprint("item_string: " + item_string)
                    magentaprint("parse output:" + str(items))

    @staticmethod
    def remove_from_qty_dict(d, duple):
        ''' For (key, qty) pairs. '''
        if duple[0] in d:
            if duple[1] >= d[duple[0]]:
                del d[duple[0]]
            else:
                d[duple[0]] -= duple[1]
        else:
            raise ValueError

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

    def parse_item_list(self, inventory_string):
        ''' Returns a dict {item: quantity} ie. {"chicken soup": 5, steel bottle: 1} '''
        return_dict = {}
        inventory_string = inventory_string.replace("\n\r", ' ')
        inv_list = inventory_string.split(',')
        inv_list = [item.strip() for item in inv_list]
        numbers = ["a ", "an ", "some ", "two ", "three ", "four ", "five ", "six ", "seven ", 
                   "eight ", "nine ", "ten ", "eleven ", "twelve ", "thirteen ", "fourteen ", 
                   "fifteen" , "sixteen ", "seventeen ", "eighteen ", "nineteen ", "twenty "]
        numbers.extend([str(i) + " " for i in range(21, 100)])

        for item in inv_list:
            for n in range(0, len(numbers)):
                number = numbers[n]
                if item[0:len(number)] == number:
                    if n < 3:
                        item = item[len(number):]
                        return_dict[item] = 1
                    else:
                        sets_of = "sets of "
                        if item[len(number):len(number)+len(sets_of)] == sets_of:
                        # if item[len(number) + (0:9)] == " sets of ":
                            item = item[len(number)+len(sets_of):]
                        else:
                            item = item[len(number):]
                            if item[len(item)-1] == 's':
                                if item[len(item)-3:] == "ses" or item[len(item)-3:] == "xes":
                                    item = item[:len(item)-2]
                                else:
                                    item = item[:len(item)-1]

                        return_dict[item] = n - 1

                    continue

        return return_dict

    def sellable(self):
        # Go backwards through the list because we want to sell in reverse order
        # That way the numbers don't change.
        # Here we are counting the items so we can come up with "silver 5" and stuff like that.

        # The word "reference" is used as a more generic term for the word "item" in case you 
        # have a large axe and a large knife, their references are both "large" 

        # This is O(like a gazillion) but that's fine with me.  It's pretty darn complicated.  
        # I dare you to come up with a better algorithm.  I bet python list operations are 
        # pretty quick.

        references = {}
        numbered_references = []

        for item in self.inventory:
            reference = self._item_string_to_reference(item)

            if item not in self.keep_list:
                prev_items_with_same_reference = references[reference] if reference in references else 0

                if prev_items_with_same_reference == 0:
                    numbered_references.append(reference)
                    numbered_references.extend([reference + " " + str(n) for n in range(1, self.inventory[item])])
                else:
                    numbered_references.extend([reference + " " + str(n) for n in range(prev_items_with_same_reference, prev_items_with_same_reference + self.inventory[item])])

            Inventory.add_to_qty_dict(references, (item, self.inventory[item]))

            # TODO: have quantities in keep_list

        numbered_references.reverse()
        return numbered_references
      
    def _item_string_to_reference(self, item_string):
        # 'grey cloak' will be "grey", it just takes the first word.
        return item_string.split(" ")[0].split(".")[0]

    restoratives = ["chicken soup", "small restorative", "small flask", 
                    "large restorative", "scarlet potion"]
    # usable = ["small retorative", "large restorative", "chicken soup", "scarlet potion", 
    #           "steel bottle", "silver chalice", "milky potion",
    #           "glowing potion",
    #           "adamantine rod", "granite rod", "zinc wand"]

    # should probably depend on level.
    #keep_list = ["small restorative", "silver chalice", "steel bottle", "milky potion"] 


    adam_keep_list = ["large bag", "large sack", 
        "silver chalice", "steel bottle", "small restorative", 'glowing potion', "chicken soup", 
        'scarlet potion', "white potion"
        # weapons
        #'war hammer', "adamantine sword", 'adamantine axe', "claymore", 
        #"spider leg", 
        #"spear", "bolos", 'javelin', "long bow", 
        #"heathen amulet",
        #"broad sword", "rapier",
        #'heavy crossbow', 
        # armour
        #"hard cap", "hard gloves", "hard boots", "padded hat",
        #"mountain gloves", "mountain boots", "mountain boots with crampons",
        #"travellers cross", "leather mask", "leather collar",
        #"studded leather collar", "studded leather sleeves",
        #"studded leather boots", "studded leather pants",
        #"chain mail armour", 'chain mail sleeves', 'chain mail leggings', 
        #'chain mail gloves', 'chain mail hood', 'chain mail boots', 
        #"ring mail armour", "ring mail sleeves", "ring mail leggings", 
        #"ring mail hood", "ring mail gauntlets", "leather collar", 
        #"furry cloak", "enchanted indigo cloak",
        #'lion charm', "poison ring",
        #'steel mask' # the bot slowly collects these
        ]

    keep_list = ["large bag", "large sack", 
        "silver chalice", "steel bottle", 
        'glowing potion', 
        "chicken soup", "small restorative", "small flask", 
        "large restorative", "scarlet potion",
        # weapons
        'war hammer', "adamantine sword", 'adamantine axe', "claymore", 
        "spider leg", 'heavy crossbow', 
        "spear", "bolos", 'javelin', "long bow", 
        "heathen amulet",
        "broad sword", "rapier",
        # armour
        "hard cap", "hard gloves", "hard boots", "padded hat",
        "mountain gloves", "mountain boots", "mountain boots with crampons",
        "travellers cross", "leather mask", "leather collar",
        "studded leather collar", "studded leather sleeves",
        "studded leather boots", "studded leather pants",
        "studded leather gloves",
        # "chain mail armour", 
        'chain mail sleeves', 'chain mail leggings', 
        'chain mail gloves', 'chain mail hood', 'chain mail boots', 
        "ring mail armour", "ring mail sleeves", "ring mail leggings", 
        "ring mail hood", "ring mail gauntlets", "leather collar", 
        "enchanted indigo cloak", "fine elven cloak", "light elven cloak",
        'lion charm', "poison ring",
        "iron shield"
        #'steel mask' # the bot slowly collects these 
        ] 

    MUD_RETURN_ITEM_SOLD = False


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
