from peewee import *
from db.BaseModel import *
from db.NamedModel import NamedModel
from misc_functions import *

class ItemTypeData(NamedModel):

    def to_string(self):
        return str(self.name)

    def get_by_name(name):
        # print('ItemTypeData get_by_name(name) ItemTypeData.name: ' + str(ItemTypeData.name) + ', arg: ' + str(name))
        try:
            # obj = ItemTypeData.select().where(fn.Lower(ItemTypeData.name) == fn.Lower(name))
            obj = ItemTypeData.select().where(ItemTypeData.name == name)
        except ItemTypeData.DoesNotExist:
            obj = None

        print('ItemTypeData get_by_name(name) returning: ' + str(obj))
        return obj