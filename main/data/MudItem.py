from peewee import *
from Database import *
from misc_functions import *

class MudItem():
    item = None
    is_unusable = False

    def __init__(self, item_name):
        self.item = Item(name=item_name)
        self.item.map()

    def to_string(self):
        #return "<" + str(self.item.id) + ">[" + self.item.name + "]"
        return self.item.name

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
        is_equal = isinstance(other, self.__class__)

        if is_equal:
            is_equal = self.item.id == other.item.id

        return is_equal

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.item.id