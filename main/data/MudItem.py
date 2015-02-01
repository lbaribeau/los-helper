from peewee import *
from Database import *
from misc_functions import *

class MudItem():
    item = None
    is_unusable = False

    def __init__(self, item_name):
        self.item = Item(name=item_name)

    def map(self):
        self.item.map()

    def to_string(self):
        #return "<" + str(self.item.id) + ">[" + self.item.name + "]"
        return self.item.name

    def __getitem__(self,key):
        return Item.get_item_by_name(key)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
        is_equal = isinstance(other, self.__class__)

        if is_equal:
            is_equal = self.item.name == other.item.name

        return is_equal

    def __lt__(self, other):
        return self.item.name < other.item.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.item.id


class ItemList():
    items = []
    qty = 1

    def __init__(self, items):
        self.items = items
        self.set_quantity()

    def add(self, item_list):
        self.items += item_list.items
        self.set_quantity()

    def remove(self, item, index=0):
        self.items.pop(index)
        self.qty -= 1

    def set_quantity(self):
        self.qty = len(self.items)        

    def to_string(self):
        return str(self.qty)

    def __int__(self):
        return self.qty

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()