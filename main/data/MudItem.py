from peewee import *
from Database import *
from misc_functions import *
from GenericMudObject import *

class MudItem(GenericMudObject):
    is_unusable = False
    item = None

    def __init__(self, name):
        self.obj = Item(name=name)
        self.reference = get_last_word(self.obj.name)

    def map(self):
        self.obj.map()

    def is_of_type(self, type_name, level=-1):
        is_of_type = False

        if self.item.itemtype is not None:
            if self.item.itemtype.model is not None:
                if self.item.itemtype.model.name is type_name:
                    is_of_type = True
                    if level is not -1:
                        if self.item.level is not None:
                            if self.item.level is not level:
                                is_of_type = False
                        else:
                            is_of_type = False

        return is_of_type

