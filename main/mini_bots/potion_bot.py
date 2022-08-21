import time
import re
# import threading
from misc_functions import *
from Exceptions import *
from mini_bots.travel_bot   import TravelBot
from mini_bots.shopping_bot import ShoppingBot
from mini_bots.mini_bot     import MiniBot
from db.Database            import AreaStoreItem

class PotionBot(MiniBot):
    def __init__(self, character, command_handler, mud_map):
        super().__init__()
        self.character = character
        self.inventory = character.inventory
        self.command_handler = command_handler
        self.shopping_bot = ShoppingBot(self.character, self.command_handler, mud_map)
        # magentaprint(str(AreaStoreItem.get_by_name('milky potion')[0].item.id) + " test", False)
        self.potion_store = AreaStoreItem.get_by_name('milky potion')[0]
    
    def run(self):
        self.stopping = False
        if self.needs_to_shop():
            self.shopping_bot.buy_with_ref(self.potion_store, 'milky')
            self.shopping_bot.buy_with_ref(self.potion_store, 'milky')
            self.shopping_bot.buy_with_ref(self.potion_store, 'milky')
            self.shopping_bot.buy_with_ref(self.potion_store, 'bottle')
            self.shopping_bot.buy_with_ref(self.potion_store, 'bottle')
            self.shopping_bot.buy_with_ref(self.potion_store, 'bottle')
        self.stop()
    
    def needs_to_shop(self):
        if self.inventory.has(['milky potion']) and self.inventory.has(['steel bottle']):
            return False
        
        return True
    
    def stop(self):
        self.stopping = True
        self.shopping_bot.stop()