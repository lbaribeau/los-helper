
from peewee import *
from db.BaseModel import BaseModel
from db.Item import Item
from db.ItemType import ItemType
from db.ItemTypeModel import ItemTypeModel
from db.ItemTypeData import ItemTypeData
from db.Area import Area
from misc_functions import *

class AreaStoreItem(BaseModel):
    area = ForeignKeyField(Area)
    item = ForeignKeyField(Item)

    '''Private AreaStoreItem Functions'''
    def map(self):
        is_new_mapping = False
        areastoreitem = AreaStoreItem.get_by_area_and_item(self.area.id, self.item.id)

        if areastoreitem is None:
            super(AreaStoreItem, self).save()
        else:
            self.id = areastoreitem.id
            self.area = areastoreitem.area
            self.item = areastoreitem.item
            #update other fields if you want

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + str(self.area.id) + ", " + str(self.item.name)

    # def get_item(self):
    #     return Item.get_by_areastoreitem(self)

    # def get_cost(self):
    #     return Item.get_by_areastoreitem(self).value

    '''Static AreaStoreItem Functions'''
    def get_by_area_and_item(areaid, itemid):
        try:
            areastoreitem = AreaStoreItem.select().where((AreaStoreItem.area == areaid) & (AreaStoreItem.item == itemid)).get()
        except AreaStoreItem.DoesNotExist:
            areastoreitem = None

        return areastoreitem

    def get_by_item(itemid):
        areastoreitem = AreaStoreItem.select().where(AreaStoreItem.item == itemid).get()

        return areastoreitem

    def get_by_item_type_and_level(model_name, data_name, level=1):
        # Here the query is for a given item level
        # Model: weapon s-armor m-armor l-armor consumable held reageant scroll quest trash armor
        # Data: Sharp Thrust Blunt Pole Missile Body Arms Legs Neck Hands Head Feet Finger Shield
        # items = []
        # itemtypemodel = ItemTypeModel.get_by_name(model_name).get().id
        # itemtypedata = ItemTypeData.get_by_name(data_name).get().id
        # print('AreaStoreItem itemtypemodel: ' + str(itemtypemodel))
        # print('AreadStoreItem itemtypemodel: %s, itemtypedata: %s' % (str(itemtypemodel), str(itemtypedata)))
        # items = AreaStoreItem.select().join(Item).where(Item.level == level).join(ItemType).where(ItemType.model == itemtypemodel and ItemType.data == itemtypedata)
        items = (AreaStoreItem
            .select()
            .join(Item)
            .where(Item.level == level)
            .join(ItemType)
            .where(
                (ItemType.model == ItemTypeModel.get_by_name(model_name).get().id) & 
                (ItemType.data  == ItemTypeData.get_by_name(data_name).get().id))
        )
        #print("AreaStoreItem get_by_item_type_and_level returning " + str(items))
        magentaprint("AreaStoreItem get_by_item_type_and_level returning " + str([i.item.name for i in items]))
        return items

    def get_by_item_type_and_level_max(model_name, data_name, level_max=1):
        # Here, the query is for a given maximum item level (returns all items less than or equal to given max item level)
        #BaseModel.magentaprint("AreaStoreItem get model_name/data_name: " + model_name + '/' + data_name + ", ids: " + str(itemtypemodel) + "/" + str(itemtypedata) )
        # (Searches general armour and sized armour)
        # Model means something of "weapon", "s-armour", "m-armour", "l-armour", "finger" , "shield", sizeless armour... also other item types (consume, held...)
        # Data means where it equips??? Not exactly... 1-5: are extended weapon types, 6-15 are where they equip
        items = (AreaStoreItem
            .select()
            .join(Item)
            .where(Item.level <= level_max)
            .join(ItemType)
            .where(
                (ItemType.model == ItemTypeModel.get_by_name(model_name).get().id) & 
                (ItemType.data == ItemTypeData.get_by_name(data_name).get().id))
            # .order_by(-Item.level)
            .order_by(-Item.value) # Prefer expensive (cant afford logic is elsewhere)... honestly only value is likely needed as it correlates with .level
        )
        # obj = NamedModel.select().where(fn.Lower(NamedModel.name) == fn.Lower(name)).get()
        #print("AreaStoreItem get_by_item_type_and_level_max returning " + str(items))
        # BaseModel.magentaprint("AreaStoreItem get_by_item_type_and_level_max returning " + str([i for i in items]))
        # Level max means you include all levels below (you supply a maximum)
        # Ok, so do we sort it? Brocolli is buying a small mace, and Alfredo doesn't have a level 3 thrusting
        magentaprint("AreaStoreItem get_by_item_type_and_level_max returning " + str([i.item.name for i in items]))
        return items

    def get_buyable_armour(size, slot, max_level=1):
        return AreaStoreItem.get_armour_by_size_location_and_level(size, slot, max_level)

    def get_armour_by_size_location_and_level(size, location, max_level=1):
        # Location is actually armour slot like legs or shield, not store location
        if size in ('s-armor', 'm-armor', 'l-armor', 'armor'):
            sized_armours = list(AreaStoreItem.get_by_item_type_and_level_max(size, location, max_level))
            if size == 'armour':
                unsized_armours = []
            else:
                unsized_armours = list(AreaStoreItem.get_by_item_type_and_level_max('armor', location, max_level))
            # BaseModel.magentaprint("AreaStoreItem.get_armour_by_size_location_and_level() sized/unsized: " + str(sized_armours) + '/' + str(unsized_armours))
            # BaseModel.magentaprint("AreaStoreItem.get_armour_by_size_location_and_level() armours:")
            # for x in sized_armours + unsized_armours:
            #     BaseModel.magentaprint(str(x))
            #BaseModel.magentaprint("AreaStoreItem.get_armour_by_size_location_and_level returning: " + str(sorted(sized_armours + unsized_armours, key=lambda a: -a.item.level)))
            return sorted(sized_armours + unsized_armours, key=lambda a: -a.item.level)
        else:
            raise Exception("AreaStoreItem.get_buyable_armour() called with invalid size.")

    def get_by_name(item_name):
        print("AreaStoreItem.get_by_name() item_name: " + str(item_name))
        items = AreaStoreItem.select().join(Item).where(Item.name == item_name)
        print("AreaStoreItem.get_by_name() returning: " + str(item_name))
        return items

    # def get_an_instance_by_name(item_name):
    #     print("AreaStoreItem.get_an_instance_by_name() item_name: " + str(item_name))
    #     asi = AreaStoreItem.select().join(Item).where(Item.name == item_name).get()
    #     print("AreaStoreItem.get_an_instance_by_name() returning: " + str(item_name))
    #     return asi

    # def gold_lookup(item_name):
    #     g = AreaStoreItem.get_an_instance_by_name(item_name).  # value is in ITEM not areastoreitem...
    #     print("AreaStoreItem.gold_lookup({}) got {}".format(item_name, g))
    #     return g

    def get_by_area(aid):
        return AreaStoreItem.select().where(AreaStoreItem.area == aid)

        # get_by_item_type_and_level() prints
        # print("AreaStoreItem.get_by_item_type_and_level(): model_name: " + str(model_name) + ", data_name: " + str(data_name) + ", level: " + str(level))
        # magentaprint("ItemTypeModel.get_by_name(model_name).get().id: " + ItemTypeModel.get_by_name(model_name).get().id)

        # print("AreaStoreItem ItemTypeModel.get_by_name(model_name).get().id: model_name: " + str(model_name) + ', data_name: ' + str(data_name))
        # print('AreaStoreItem ItemTypeModel: ' + str(ItemTypeModel))
        # print('AreaStoreItem ItemTypeModel get_by_name: ' + str(ItemTypeModel.get_by_name(model_name)))
        # myitemtypemodel = ItemTypeModel.get_by_name(model_name)
        # # print('AreaStoreItem itemtypemodel: ' + str(ItemTypeModel.get_by_name(model_name).get()))  # This one
        # print('AreaStoreItem itemtypemodel: ' + str(myitemtypemodel.get()))  # This one
        # print('AreaStoreItem itemtypemodel.id: ' + str(ItemTypeModel.get_by_name(model_name).get().id))



