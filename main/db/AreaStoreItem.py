from peewee import *
from db.BaseModel import *
from db.Item import *
from db.ItemType import *
from db.ItemTypeModel import *
from db.ItemTypeData import *
from db.Area import *
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

    '''Static AreaStoreItem Functions'''
    def get_by_area_and_item(areaid, itemid):
        try:
            areastoreitem = AreaStoreItem.select().where((AreaStoreItem.area == areaid and AreaStoreItem.item == itemid)).get()
        except AreaStoreItem.DoesNotExist:
            areastoreitem = None

        return areastoreitem

    def get_by_item(itemid):
        try:
            areastoreitem = AreaStoreItem.select().where((AreaStoreItem.item == itemid)).get()
        except AreaStoreItem.DoesNotExist:
            areastoreitem = None

        return areastoreitem

    def get_by_item_type_and_level(model_name, data_name, level = 1):
        items = []

        itemtypemodel = ItemTypeModel.get_by_name(model_name).get().id
        itemtypedata = ItemTypeData.get_by_name(data_name).get().id

        try:
            items = AreaStoreItem.select().join(Item).where(Item.level == level).join(ItemType).where(ItemType.model == itemtypemodel and ItemType.data == itemtypedata)
        except AreaStoreItem.DoesNotExist:
            items = []

        return items