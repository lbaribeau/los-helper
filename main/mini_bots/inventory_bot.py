
from mini_bots.mini_bot import MiniBot

class InventoryBot(MiniBot):
    def __init__(self, inv, commandHandler):
        self.inv = inv

    def sell_stuff(self):
        self.__stopping = False
        # self.get_inventory()  # Unnecessary if inventory is well tracked

        for item_ref in self.sellable():
            if not self.__stopping:
                self.sell(item_ref)
            else:
                return


    def drop_stuff(self):

    def drop_unusable_weapons(self):

    def sell_list(self):

    def drop_list(self):

