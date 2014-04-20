
import time
import re

from Exceptions import *
from BotReactions import *
from misc_functions import *


class Inventory(BotReactionWithFlag):

    def __init__(self, mudReaderHandler, telnetHandler):
        self.you_have = "(?s)You have: (.+?)\."
        self.wont_buy = "The shopkeep says, \"I won't buy that rubbish from you\.\""
        self.sold = "The shopkeep gives you (.+?) gold for (.+?)\."
        self.dropped = "(?s)You drop (.+?)\.\n\rThanks for recycling\.\n\rYou have (.+?) gold\."
        self.not_a_pawn_shop = "This is not a pawn shoppe\."
        self.you_now_have = "You now have (.+?) gold pieces\."
        self.not_empty = "It isn't empty!"
        self.you_wear= "(?s)You wear (.+?)\."
        self.nothing_to_wear = "You have nothing you can wear\."
        self.you_get = "You get (.+?)\."
        self.you_remove = "(?s)You removed? (.+?)\."
        self.nothing_to_remove = "You aren't wearing anything that can be removed\."
        self.you_wield = "You wield (.+?)\."
        self.you_give = "You give (.+?) to (.+?)\."
        self.bought = "Bought\."  
        self.you_put_in_bag = "You put (.+?) into (.+?)\."

        super(Inventory, self).__init__([self.you_have, self.you_get, self.wont_buy, self.sold, 
            self.dropped, self.not_a_pawn_shop, self.you_now_have,
            self.not_empty, self.you_wear, self.nothing_to_wear, self.you_remove,  
            self.nothing_to_remove, self.you_wield, self.you_give, self.bought,
            self.you_put_in_bag])

        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.inventory = []
        self.gold = 0
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex is self.you_have:
            self.set_inventory(M_obj.group(1))
            # magentaprint(str(self.inventory))
        elif regex is self.sold:
            self.gold = self.gold + int(M_obj.group(1))
            self.remove(M_obj.group(2))
        elif regex is self.dropped:
            self.remove(M_obj.group(1))
            self.gold = int(M_obj.group(2))
        elif regex is self.you_now_have:
            self.gold = int(M_obj.group(1))
        elif regex is self.you_wield:
            weapon = self.clip_in_your_off_hand(M_obj.group(1))
            self.remove(weapon)
        elif regex is self.you_get:
            item = self.clip_from_a_container(M_obj.group(1))
            self.add(item)
        elif regex is self.you_wear or regex is self.you_give or regex is self.you_put_in_bag:
            self.remove(M_obj.group(1))
        elif regex is self.you_remove:
            self.add(M_obj.group(1))
        elif regex is self.bought:
            self.get_inventory()  # There are some notes about this at the bottom

        super(Inventory, self).notify(regex, M_obj)  # sets __waiter_flag

    def get_inventory(self):
        self.telnetHandler.write("i")
        self.wait_for_flag()
        return self.inventory

    def get_number_of_items(self, item):
        return self.inventory.count(item)

    def sell_stuff(self):
        self.__stopping = False
        self.get_inventory()  # Unnecessary if inventory is well tracked

        for item in self.sellable():
            if not self.__stopping:
                self.sell(item)
            else:
                return

    def sell(self, item):
        self.telnetHandler.write("sell " + item)
        self.wait_for_flag()

    # def sell_fast(self):

    def drop_stuff(self):
        self.__stopping = False
        self.get_inventory()  # Unnecessary if sell manages to match everything.

        for item in self.sellable():
            if not self.__stopping:
                self.drop(item)
            else:
                return

    def drop(self, item):
        self.telnetHandler.write("drop " + item)
        self.wait_for_flag()

    def drop_fast(self):
        pass

    def give(self, item, target):
        pass

    def put_in_sack(self, item, sack):
        pass

    def stop(self):
        self.__stopping = True

    def set_inventory(self, item_string):
        self.inventory = self.parse_inventory_list(item_string)

    def add(self, item_string):
        self.inventory.extend(self.parse_inventory_list(item_string))
        self.inventory.sort()

    def remove(self, item_string):
        for i in self.parse_inventory_list(item_string):
            try: 
                self.inventory.remove(i)
            except ValueError:
                magentaprint("Couldn't remove " + i + " from inventory.", False)
                magentaprint("inventory:" + str(self.inventory), False)
                magentaprint("item_string: " + item_string, False)
                magentaprint("parse output:" + str(self.parse_inventory_list(item_string)), False)
                magentaprint("problem item: " + i, False)

    def remove_a_an_some(self, aString):
        if aString[0:2] == "a ":
            aString = aString[2:]
        elif aString[0:3] == "an ":
            aString = aString[3:]
        elif aString[0:5] == "some ":
            aString = aString[5:]

        return aString

    def clip_in_your_off_hand(self, wield_string):
        length = len(wield_string)

        if wield_string[length-17:length] == " in your off hand":
            return wield_string[:length-17]
        else:
            return wield_string

    def clip_from_a_container(self, get_string):
        M_obj = re.search("(.+?) from (.+?)", get_string)

        if M_obj != None:
            magentaprint("returning: " + M_obj.group(1))
            return M_obj.group(1)
        else:
            magentaprint("returning: " + get_string)
            return get_string


    def parse_inventory_list(self, inventory_string):
        return_list = []
        inventory_string = replace_newlines_with_spaces(inventory_string)
        inv_list = inventory_string.split(',')
        inv_list = [item.lstrip() for item in inv_list]
        inv_list = [item.rstrip() for item in inv_list]
        numbers = ["a ", "an ", "some ", "two ", "three ", "four ", "five ", "six ", "seven ", 
                   "eight ", "nine ", "ten ", "eleven ", "twelve ", "thirteen ", "fourteen ", 
                   "fifteen" , "sixteen ", "seventeen ", "eighteen ", "nineteen ", "twenty "]
        numbers.extend([str(i) for i in range(21, 100)])

        for item in inv_list:
            for n in range(0, len(numbers)):
                number = numbers[n]
                if item[0:len(number)] == number:
                    if n < 3:
                        item = item[len(number):]
                        return_list.append(item)
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

                        for _ in range(0, n-1):
                            return_list.append(item)

                    continue

        return return_list



    def sellable(self):
        # Go backwards through the list because we want to sell in reverse order
        # That way the numbers don't change.
        # Here we are counting the items so we can come up with "silver 5" and stuff like that.

        # The word "reference" is used as a more generic term for the word "item" in case you 
        # have a large axe and a large knife, their references are both "large" 

        references = []
        numbered_references = []

        for i in range(0, len(self.inventory)):
            reference = self._item_string_to_reference(self.inventory[i])
            references.append(reference)

            if self.inventory[i] not in self.keep_list:
                prev_items_with_same_reference = references.count(reference) - 1
                if(prev_items_with_same_reference == 0):
                    numbered_references.append(reference)
                else:
                    numbered_references.append(reference + " " + str(prev_items_with_same_reference + 1))

        numbered_references.reverse()
        return numbered_references
      

    def _item_string_to_reference(self, item_string):
        # 'grey cloak' will change to 'grey'
        # It just takes the first word.
        return item_string.split(" ")[0].split(".")[0]


    # should probably depend on level.
    keep_list = ["large bag", "large sack", 
        "silver chalice", "steel bottle", "small restorative", 'heavy crossbow', 
        'glowing potion', "chicken soup",
        # weapons
        'war hammer', "adamantine sword", 'adamantine axe', "claymore", 
        "spider leg", 
        "spear", "bolos", 'javelin', "long bow", 
        "heathen amulet",
        "broad sword", "rapier",
        # armour
        "hard cap", "hard gloves", "hard boots", "padded hat",
        "mountain gloves", "mountain boots", "mountain boots with crampons",
        "travellers cross", "leather mask", "leather collar",
        "studded leather collar", "studded leather sleeves",
        "studded leather boots", "studded leather pants",
        "chain mail armour", 'chain mail sleeves', 'chain mail leggings', 
        'chain mail gloves', 'chain mail hood', 'chain mail boots', 
        "ring mail armour", "ring mail sleeves", "ring mail leggings", 
        "ring mail hood", "ring mail gauntlets", "leather collar", 
        "furry cloak", "enchanted indigo cloak",
        'lion charm', "poison ring",
        'scarlet potion'
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

