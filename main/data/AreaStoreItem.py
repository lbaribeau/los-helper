from peewee import *
from BaseModel import *
from misc_functions import *
from Item import *
from Area import *

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
        return str(self.id) + ", " + str(self.area) + ", " + str(self.item)

    '''Static AreaStoreItem Functions'''
    def get_by_area_and_item(areaid, itemid):
        try:
            areastoreitem = AreaStoreItem.select().where((AreaStoreItem.area == areaid and AreaStoreItem.item == itemid)).get()
        except AreaStoreItem.DoesNotExist:
            areastoreitem = None

        return areastoreitem