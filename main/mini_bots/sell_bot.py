
import time

import misc_functions
from misc_functions import magentaprint
from mini_bots.travel_bot import TravelBot
from mini_bots.mini_bot import MiniBot
from reactions.referencing_list import ReferencingList

# class SmithyBot(Thread):
class SellBot(MiniBot):
    # keep_list = ["large bag", "large sack", "black bag",
    #     "silver chalice", "steel bottle", 'glowing potion',
    #     "chicken soup", 'scarlet potion', 'white potion', "tree root",
    #     "Elixir of Morinva", "granite potion", "philtre of perception",
    #     "burnt ochre potion", "milky potion"]

    # def __init__(self, char, command_handler, mud_map):
    def __init__(self, inventory, sell, drop):
        super().__init__()
        # self.command_handler = command_handler  # We should create a "BasicCommandHandler" to eliminate this circular dependence
        self.inventory = inventory
        self.sell = sell
        self.drop = drop
        # (CommandHandler makes bots who need to use CommandHandler - instead they can use BasicCommandHandler which can't make bots)
        # self.smartCombat = command_handler.smartCombat
        # (Hopefully won't need combat)
        # self.equipment = Equipment()
        # self.bulk_sell_bot = BulkSell()
        # self.map = mud_map
        # self.travel_bot = TravelBot(self.char, self.command_handler, mud_map)
        # Ok if we don't give this the map, then we don't need to wait for the map to get the sell list
        # May as well have travel bot do the traveling
        # This bot can bulk sell and sell from the list
        # Ok, let's not have this bot worry about the map
        # Plan is - caller gets travel bot to do the traveling part, and this bot to do the selling part
        # Travel bot can learn where the various locations are

    # def stop(self):
    #     super().stop()  # Unnecessary since travel_bot is the only loop
    #     self.travel_bot.stop()

    def run(self):
        # Parent implements start_thread() which makes a thread for this.
        # self.go_sell()
        self.sell_stuff()

    # def is_alive(self):
    #     if self.travel_bot:
    #         return self.
    #     return True

    # def go_sell(self):
    #     if self.go_to_nearest_pawn_shop() and not self.stopping:
    #         self.sell_stuff()
    #     else:
    #         raise Exception("SellBot travel error.")

    # def sell_one(self):
    #     self.command_handler.sell.execute_and_wait()
    def sellable(self):
        # We could take the keep list out of inventory
        self.inventory.get_inventory() # This line isn't necessary if we assume everything is always works perfectly
        return self.sellable_assuming_correctness()

    def sellable_assuming_correctness(self):
        self.keep_list=self.inventory.keep_list
        slist = self.inventory.get_unique_references(self.keep_list)
        slist.reverse()
        # magentaprint("Sellable items: " + str(slist)) # This is a good print that shows ie. ['the', 'sabre']
        # magentaprint("Sellable items: " + str(ReferencingList([self.inventory.get(i) for i in slist if self.inventory.get(i) is not None]))) 
        # # Ok program that defensively (if not None)
        # magentaprint("Keeping items: " + str(ReferencingList(
        #     [i for i in self.inventory.list if i in self.keep_list and i != None])))
        # get_inventory now prints all that nice stuff
        self.sell.telnetHandler.write('')
        # Can't make a referencing list with None, right...
        # return self.inventory.get_unique_references(self.keep_list)
        return slist
        #https://www.geeksforgeeks.org/python-intersection-two-lists/

    def sell_stuff(self):
        self.sell_or_drop_stuff(self.sell)
    def drop_stuff(self):
        self.sell_or_drop_stuff(self.drop)
    def sell_or_drop_stuff(self, command_object):
        # We can do things in reverse order like inventory did
        self.stopping = False
        # self.get_inventory()  # Unnecessary if inventory is well tracked
          # also - sellable does this

        for item_ref in self.sellable():
            if self.stopping:
                break
            else:
                command_object.execute_and_wait(item_ref)

        for item_ref in self.inventory.broken_junk():
            if self.stopping:
                break
            else:
                command_object.execute_and_wait(item_ref)

    def bulk_drop(self, unique_word, qty='all'):
        self.bulk_drop_or_sell(self.drop, unique_word, qty)
    def bulk_sell(self, unique_word, qty='all'):
        bulk_drop_or_sell(self.sell, unique_word, qty)
    def bulk_drop_or_sell(self, command_object, unique_word, quantity):
        # Suppose they say bdrop scarlet... let's just get all of one type of item
        self.stopping = False

        if quantity == 'all':
            if self.inventory.get(unique_word) is None:
                quantity = 0
            else:
                quantity = self.inventory.count(self.inventory.get(unique_word).name)
                # This just takes the first hit from unique_word and bulks that out

        # while item_name in self.inventory.list
        for i in range(quantity):
            if self.stopping:
                break
            else:
                command_object.execute_and_wait(unique_word)
