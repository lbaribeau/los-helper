from peewee import *

from db.NamedModel import NamedModel
from db.BaseModel import *
from misc_functions import *

class ItemTypeModel(NamedModel):

    def to_string(self):
        return str(self.name)

    def get_by_name(name):
        print("ItemTypeModel.get_by_name() name: " + str(name))
        print("ItemTypeModel name: " + str(ItemTypeModel.name))
        print("ItemTypeModel fn: " + str(fn))
        print("ItemTypeModel obj: " + ItemTypeModel.select().where(ItemTypeModel.name == name))
        try:
            # obj = ItemTypeModel.select().where(fn.Lower(ItemTypeModel.name) == fn.Lower(name))
            obj = ItemTypeModel.select().where(ItemTypeModel.name == name)
        except ItemTypeModel.DoesNotExist:
            obj = None

        return obj