
from mini_bots.mini_bot import MiniBot
from reactions.referencing_list import ReferencingList
from combat.mob_target_determinator import MobTargetDeterminator
from db.AreaStoreItem import AreaStoreItem
from mini_bots.travel_bot import TravelBot

class ShoppingBot(MiniBot):
    def __init__(self, char, command_handler, mrh, mud_map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        self.travel_bot = TravelBot(self.char, self.command_handler, mrh, mud_map)

    def stop(self):
        self.travel_bot.stop()

    def go_buy(self, asi):
        self.travel_bot.go_to_area(asi.area.id)
        return self.buy_from_shop(asi)

    def buy_from_shop(self, asi):
        # i = str(asi)
        # menu = AreaStoreItem.get_by_area_area(asi.area)
        menu = sorted(AreaStoreItem.get_by_area(asi.area), key=lambda a : a.item.name)  # Doubt this will work, but we need it sorted
        item_names = ReferencingList([asi_for_sale.item.name for asi_for_sale in menu])

        # We have (s), (m), and (l) to deal with.  Item names are alphabetical, but small, medium, large are in that order.
        if asi.item.itemtype.data.name == 'armor' or item_names.count(asi.item.name) == 1 or asi.item.itemtype.data.name == 's-armor':
            return self.buy_with_ref(asi.item.name, item_names.get_first_reference(asi.item.name))
        elif asi.item.itemtype.data.name == 'l-armor':
            return self.buy_with_ref(asi.item.name, item_names.get_last_reference(asi.item.name))
        elif asi.item.itemtype.data.name == 'm-armor':
            # If menu contains a large, then we still need first ref, if a small, then we need firstref+1
            if any(i.name == asi.item.name and i.data.name == 's-armor' for i in menu):
                return self.buy_with_ref(asi.item.name, MobTargetDeterminator().increment_ref(item_names.get_first_reference(asi.item.name)))
            else:
                return self.buy_with_ref(asi.item.name, item_names.get_first_reference(asi.item.name))
        else:
            return self.buy_with_ref(asi.item.name, item_names.get_first_reference(asi.item.name))

    def buy_with_ref(self, item_name, ref):
        self.command_handler.buy.execute_and_wait(ref)
        if self.command_handler.buy.success:
            self.char.inventory.add(item_name)
            return True
        else:
            return False
