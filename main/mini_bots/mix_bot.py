import time
import re
from misc_functions import *
from Exceptions import *
from mini_bots.shopping_bot import ShoppingBot
from mini_bots.mini_bot     import MiniBot
from db.Database            import AreaStoreItem

class MixBot(MiniBot):
    def __init__(self, character, hold, mix, remove, drop):
        super().__init__()
        self.hold = hold
        self.mix = mix
        self.remove = remove
        self.drop = drop
        self.character = character
        self.inventory = character.inventory
        # self.shopping_bot = ShoppingBot(self.character, self.command_handler, mud_map)
        # self.herb_store = AreaStoreItem.get_by_name('tree root')[0]
        self.aura_pots_count = 0
    
    def run(self, target, reageant, quantity):
        self.stopping = False
        # magentaprint("running mix bot", False)
        # self.shopping_bot.buy_with_ref(self.herb_store, 'berry')
        # for _ in range(self.aura_pots_count, 10):
        #     magentaprint("buying root", False)
        #     self.shopping_bot.buy_with_ref(self.herb_store, 'root')

        # item will be moved to the end of the list so as long as they're all ok to mix
        # then we can repeat this with no worries
        for _ in range(quantity):
            self.do_mix(target, reageant)
        self.stop()
    
    def do_mix(self, target, reageant):
        self.hold.execute_and_wait(target)
        self.mix.execute_and_wait(reageant, timeout=15.0)
        self.remove.execute_and_wait(target)
    
    def stop(self):
        self.stopping = True