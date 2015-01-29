from peewee import *
from BaseModel import *
from misc_functions import *
from Area import *

class AreaStore(BaseModel):
    area = ForeignKeyField(Area)

    '''Private AreaStore Functions'''
    def map(self):
        is_new_mapping = False
        areastore = AreaStore.get_store_by_area_id(self.area_id)

        if areastore is None:
            super(AreaStore, self).save()
        else:
            self.id = areastore.id
            self.area = areastore.area
            #update other fields if you want

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + str(self.area)

    '''Static AreaStore Functions'''
    def get_store_by_area_id(areaid):
        try:
            areastore = AreaStore.select().where((AreaStore.areaid == areaid)).get()
        except AreaStore.DoesNotExist:
            areastore = None

        return areastore