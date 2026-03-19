
from peewee import *
from db.NamedModel import NamedModel
from db.ItemType import *
from misc_functions import *

class Item(NamedModel):
    description = CharField(null=True)    # Could be 's' for small
    level       = IntegerField(null=True) # Weapons and armour have different level brackets, ie. tier 2 weapons unlocked at 40% weapon skill
    itemtype    = ForeignKeyField(ItemType, null=True) # Unique integers assigned for each kind of item, weapon types, armour types (with fanouts for size), consumable type
    value       = IntegerField(null=True) # Could be store gold cost
    # 'name' inherited by NamedModel

    '''Private Item Functions'''
    def map(self):
        # Suppose we are given name=item_name, value=item_value, description=item_size
        # It'd be nice to get the correct armour by size
        # if hasattr(self, 'name') and hasattr(self, 'value') and hasattr(self, 'description'):
            # Ok well we don't know yet if this query will work... maybe just write map_armour for this case

        item = Item.get_item_by_name(self.name) # Ehrm might have to support... armour sizes

        if item is None:
            super(Item, self).save()
            return True # is a new mapping
        else:
            self.id          = item.id
            self.level       = item.level
            self.description = item.description
            self.itemtype    = item.itemtype
            self.value       = item.value
            #update other fields if you want
            return False

    # def map_armour(self):
    #     # Assumes we have name, value, and description, which is size
    #     # The idea is that it seems like "map" really relies on .name
    #     # But there can be a few armours of same name with different sizes
    #     # So, call this function if we have description set with small/medium/large

    #     # Seems like these map functions,
    #     # -- get item from db if match exists
    #     # -- saves item to db if match doesn't exist
    #     return self.map_given_name_and_description()

    def map_given_name_and_description(self):
        # See .get_item_by_name (reference)
        item=Item.get_item_by_name_and_description(self.name, self.description)

        if item is None:
            # Save item in DB if no entry exists
            super(Item, self).save()
            return True
        else:
            self.id          = item.id
            self.level       = item.level
            self.description = item.description
            self.itemtype    = item.itemtype
            self.value       = item.value
            #update other fields if you want
            return False

    def to_string(self):
        return str(self.id) + ", " + str(self.name) + ", " + str(self.itemtype)

    '''Static Item Functions'''

    def get_item_by_name(name):
        # Called by map
        try:
            item = Item.select().where((Item.name == name)).get()
        except Item.DoesNotExist:
            item = None

        return item

    def get_item_by_name_and_description(name, description):
        magentaprint(f"Called .get_item_by_name_and_description with name and description: {name}, {description}")
        # New
        try:
            # return Item.select().where((Item.name == name) & Item.description == description).get() precedence error! Need the brackets!
            return Item.select().where((Item.name == name) & (Item.description == description)).get()
                   # Item.select().where((Item.name == 'studded leather leggings') & (Item.description == 'l')).get()
                   # exec print(str(Item.select().where((Item.name == 'studded leather leggings') & (Item.description == 'l')).get()))
        except Item.DoesNotExist:
            return None
        # item = Item.get_item_by_name(self.name) # Ehrm might have to support... armour sizes
        # return None

    def get_by_name(item_name):
        return Item.get_item_by_name(item_name)

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

    def gold_lookup(item_name):
        i = Item.get_by_name(item_name)
        if i and hasattr(i, "value"):
            print("Item.gold_lookup({}) got {}".format(item_name, i.value))
            return i.value
        else:
            print("Item.gold_lookup({}) got NOTHING! NOTHING!!!")
            print("(got {})".format(i))
            return None

