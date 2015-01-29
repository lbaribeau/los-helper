from peewee import *
from BaseModel import *
from misc_functions import *
from Item import *

class AreaStoreItem(BaseModel):
    areastore = ForeignKeyField(AreaStore)
    item = ForeignKeyField(Item)

    '''Private AreaStoreItem Functions'''
    def map(self):
        is_new_mapping = False
        areastoreitem = AreaStoreItem.get_by_areastore_and_item(self.areastore.id, self.item.id)

        if areastoreitem is None:
            super(AreaStoreItem, self).save()
        else:
            self.id = areastoreitem.id
            self.area = areastoreitem.area
            #update other fields if you want

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + str(self.area)

    '''Static AreaStoreItem Functions'''
    def get_store_by_area_id(areastoreid, itemid):
        try:
            areastoreitem = AreaStoreItem.select().where((AreaStoreItem.areastore == areastoreid and AreaStoreItem.item == itemid)).get()
        except AreaStoreItem.DoesNotExist:
            areastoreitem = None

        return areastoreitem