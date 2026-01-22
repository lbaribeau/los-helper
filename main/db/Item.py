
from peewee import *
from db.NamedModel import NamedModel
from db.ItemType import *
from misc_functions import *

class Item(NamedModel):
    description = CharField(null=True)
    level       = IntegerField(null=True)
    itemtype    = ForeignKeyField(ItemType, null=True)
    value       = IntegerField(null=True)

    '''Private Item Functions'''
    def map(self):
        is_new_mapping = False
        item = Item.get_item_by_name(self.name)

        if item is None:
            super(Item, self).save()
        else:
            self.id          = item.id
            self.level       = item.level
            self.description = item.description
            self.itemtype    = item.itemtype
            self.value       = item.value
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

    def lookup_armour_type(armour_name):
        # Ehrm Item.magentaprint doesn't work BTW
        # get_item_by_name can do this
        print("Item.lookup_armour_type armour_name: " + str(armour_name))
        atype = Item.select().where((Item.name == armour_name)).get()
        print("Item.lookup_armour_type atype: " + str(atype))
        # # "Type" is an amalgamation of "model" and "data", data being what we want, and model being small/medium/large
        # itemtype = ItemType.select().where(ItemType.id == atype.itemtype.id).get()
        # Item.magentaprint("Item.lookup_armour_type itemtype: " + str(itemtype))
        # itemdata = ItemTypeData.select().where(ItemTypeData.id == itemtype.data).get()
        # Item.magentaprint("Item.lookup_armour_type itemtypedata: " + str(itemdata))

        print("Item.lookup_armour_type atype.itemtype.data: " + str(atype.itemtype.data))
        # return str(atype.itemtype.data).lower()
        return atype.itemtype.data

    # def get_by_id(id):
    #     try:
    #         item = Item.select().where((Item.id == id)).get()
    #     except Item.DoesNotExist:
    #         item = None

    #     return item

    # def get_by_areastoreitem(asi):
    #     try:
    #         item = Item.select().where((Item.id == asi.item)).get()
    #     except Item.DoesNotExist:
    #         item = None

    #     return item
    # Didn't need these functions ^ ... I had .value == None because dBeaver had connections to wrong database files open

    def get_by_name(item_name):
        return Item.get_item_by_name(item_name)

    def gold_lookup(item_name):
        i = Item.get_by_name(item_name)
        if i and hasattr(i, "value"):
            print("Item.gold_lookup({}) got {}".format(item_name, i.value))
            return i.value
        else:
            print("Item.gold_lookup({}) got NOTHING! NOTHING!!!")
            print("(got {})".format(i))
            return None

