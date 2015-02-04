from peewee import *
from NamedModel import NamedModel
from misc_functions import *
from ItemType import *

class Item(NamedModel):
    description = CharField(null=True)
    level = IntegerField(null=True)
    itemtype = ForeignKeyField(ItemType, null=True)
    value = IntegerField(null=True)

    '''Private Item Functions'''
    def map(self):
        is_new_mapping = False
        item = Item.get_item_by_name(self.name)

        if item is None:
            super(Item, self).save()
        else:
            self.id = item.id
            self.level = item.level
            self.description = item.description
            self.itemtype = item.itemtype
            self.value = item.value
            #update other fields if you want

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + str(self.name) + ", " + str(self.itemtype)

    '''Static Item Functions'''
    def get_item_by_name(name):
        try:
            item = Item.select().where((Item.name == name)).get()
        except Item.DoesNotExist:
            item = None

        return item