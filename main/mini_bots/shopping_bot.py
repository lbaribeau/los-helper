
from mini_bots.mini_bot import MiniBot
from reactions.referencing_list import ReferencingList
from combat.mob_target_determinator import MobTargetDeterminator
from db.AreaStoreItem import AreaStoreItem
from mini_bots.travel_bot import TravelBot
from mini_bots.sell_bot import SellBot
from misc_functions import magentaprint

class ShoppingBot(MiniBot):
    def __init__(self, char, command_handler, mud_map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        self.travel_bot = TravelBot(self.char, self.command_handler, mud_map)
        self.sell_bot = SellBot(self.char.inventory, self.command_handler.sell, self.command_handler.drop)

    def stop(self):
        super().stop()
        self.travel_bot.stop()

    def cant_afford(self, asi):
        # Item.get_item_by_name(asi.item
        if asi.item.value:
            return asi.item.value > self.char.GOLD
        else:
            magentaprint("Warning: Database should really have 'value' (cost) assigned for " + asi.item.name)
        # return asi.get_cost() > self.char.GOLD

    def go_buy(self, asi):
        self.stopping = False
        magentaprint("ShoppingBot starting Travel bot to buy " + str(asi.item.name))
        # Let's put a check in here right???? If can't afford... ohhhh crappp only the bot knows that!!! That's executive...
        # No we ARE a bot we have command handler
        magentaprint(asi.item.value)
        # Oooofff a bunch of debugging because DBeaver was showing me the wrong database... "value" hadn't written
        if self.cant_afford(asi):
            magentaprint("Can't afford " + str(asi.item.name))
            return False

        self.travel_bot.go_to_area(asi.area.id)

        if self.stopping:
            return
        else:
            success = self.buy_from_shop(asi)
            if success and asi.item.value:
                self.char.GOLD -= asi.item.value # Does this happen? Could do this at buy_with_ref level
                magentaprint("Shopping bot reduced GOLD to " + str(self.char.GOLD))
            return success

    def buy_from_shop(self, asi):
        # Alright well we check here too... because armour bot is doing its own traveling... 
        return self.buy_with_ref(asi, self.choose_reference(asi))

    def buy_with_ref(self, asi, ref):
        self.stopping = False
        self.command_handler.buy.execute_and_wait(ref)
        if self.command_handler.buy.success:
            self.char.inventory.add(asi.item.name) # It's a bit hard for buy to do this part
            # self.char.GOLD -= asi.item.value
            return True
        else:
            if self.command_handler.buy.no_gold:
                magentaprint("ShoppingBot saw no_gold.")
                raise
            else:
                # Ok go sell stuff then (assumes overburdened)
                if self.stopping:
                    return
                self.travel_bot.go_to_nearest_pawn_shop()
                if self.stopping:
                    return
                self.sell_bot.sell_stuff()
                if self.stopping:
                    return
                self.travel_bot.go_to_nearest_tip()
                if self.stopping:
                    return
                self.sell_bot.drop_stuff()
                if self.stopping:
                    return
                self.travel_bot.go_to_area(asi.area.id)
                if self.stopping:
                    return
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
