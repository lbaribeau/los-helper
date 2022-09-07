
from mini_bots.mini_bot import MiniBot
from reactions.referencing_list import ReferencingList
from combat.mob_target_determinator import MobTargetDeterminator
from db.AreaStoreItem import AreaStoreItem
from mini_bots.travel_bot import TravelBot
from mini_bots.sell_bot import SellBot

class ShoppingBot(MiniBot):
    def __init__(self, char, command_handler, mud_map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        self.travel_bot = TravelBot(self.char, self.command_handler, mud_map)
        self.sell_bot = SellBot(self.char.inventory, self.command_handler.sell, self.command_handler.drop)

    def stop(self):
        self.travel_bot.stop()

    def go_buy(self, asi):
        self.stopping = False
        self.travel_bot.go_to_area(asi.area.id)
        if self.stopping:
            return
        else:
            return self.buy_from_shop(asi)

    def buy_from_shop(self, asi):
        return self.buy_with_ref(asi, self.choose_reference(asi))

    def buy_with_ref(self, asi, ref):
        self.command_handler.buy.execute_and_wait(ref)
        if self.command_handler.buy.success:
            self.char.inventory.add(asi.item.name) # It's a bit hard for buy to do this part
            return True
        else:
            # Ok go sell stuff then
            self.travel_bot.go_to_nearest_pawn_shop()
            self.sell_bot.sell_stuff()
            self.travel_bot.go_to_nearest_tip()
            self.sell_bot.drop_stuff()
            self.travel_bot.go_to_area(asi.area.id)
            self.command_handler.buy.execute_and_wait(ref)
            if self.command_handler.buy.success:
                self.char.inventory.add(asi.item.name)
                return True
            else:
                self.sell_bot.bulk_drop('scarlet')
                self.sell_bot.bulk_drop('flask')
                if self.char.inventory.has('steel bottle'):
                    # self.command_handler.telnetHandler.write('drin ' + self.char.inventory.get_reference('steel bottle'))
                    # self.command_handler.use.command = 'drin'
                    # self.command_handler.use.execute_and_wait(self.char.inventory.get_reference('steel bottle'))
                    # self.command_handler.use.command = 'use'
                    self.command_handler.drink.execute_and_wait(self.char.inventory.get_reference('steel bottle'))
                self.sell_bot.bulk_drop('bottle') # Hopefully no valuable "bottles"
                # Otherwise, write bulk drop that takes full item name
                self.command_handler.buy.execute_and_wait(ref) # ref is a reference to a shop item so it doesn't depend on inventory
                # We might have too many weapons, that can happen right now
                self.command_handler.telnetHandler.write('get all')
                if self.command_handler.buy.success:
                    self.char.inventory.add(asi.item.name)
                    return True
                else:
                    raise

    def choose_reference(self, asi):
        # i = str(asi)
        # menu = AreaStoreItem.get_by_area_area(asi.area)
        menu = sorted(AreaStoreItem.get_by_area(asi.area), key=lambda a : a.item.name)
        item_names = ReferencingList([asi_for_sale.item.name for asi_for_sale in menu])

        # We have (s), (m), and (l) to deal with.  Item names are alphabetical, but small, medium, large are in that order.
        if asi.item.itemtype.data.name == 'armor' or item_names.count(asi.item.name) == 1 or asi.item.itemtype.data.name == 's-armor':
            return item_names.get_first_reference(asi.item.name)
        elif asi.item.itemtype.data.name == 'l-armor':
            return item_names.get_last_reference(asi.item.name)
        elif asi.item.itemtype.data.name == 'm-armor':
            # If menu contains a large, then we still need first ref, if a small, then we need firstref+1
            if any(i.name == asi.item.name and i.data.name == 's-armor' for i in menu):
                return MobTargetDeterminator().increment_ref(item_names.get_first_reference(asi.item.name))
            else:
                return item_names.get_first_reference(asi.item.name)
        else:
            return item_names.get_first_reference(asi.item.name)
