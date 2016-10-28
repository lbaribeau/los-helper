
from mini_bots.mini_bot import MiniBot
from reactions.referencing_list import ReferencingList
from combat.mob_target_determinator import MobTargetDeterminator

class ShoppingBot(MiniBot):
    def __init__(self, char, command_handler):
        super().__init__()
        self.char = char
        self.command_handler = command_handler

    def buy_from_shop(self, item):
        # i = str(item)
        # menu = AreaStoreItem.get_by_area_area(item.area)
        menu = sorted(AreaStoreItem.get_by_area(item.area), key=lambda a : a.item.name)  # Doubt this will work, but we need it sorted
        item_names = ReferencingList([asi.item.name for asi in menu])

        # We have (s), (m), and (l) to deal with.  Item names are alphabetical, but small, medium, large are in that order.
        if item.data.name == 'armor' or item_names.count(item.name) == 1 or item.data.name == 's-armor':
            self.buy_with_ref(item.name, item_names.get_first_reference(item.name))
        elif item.data.name == 'l-armor':
            self.buy_with_ref(item.name, item_names.get_last_reference(item.name))
        elif item.data.name == 'm-armor':
            # If menu contains a large, then we still need first ref, if a small, then we need firstref+1
            if any(i.name == item.name and i.data.name == 's-armor' for i in menu):
                self.buy_with_ref(item.name, MobTargetDeterminator().increment_ref(item_names.get_first_reference(item.name)))
            else:
                self.buy_with_ref(item.name, item_names.get_first_reference(item.name))
        else:
            self.buy_with_ref(item.name, item_names.get_first_reference(item.name))

    def buy_with_ref(self, item_name, ref):
        self.command_handler.buy.execute_and_wait(ref)
        if command_handler.buy.success:
            self.char.inventory.add(item_name)
