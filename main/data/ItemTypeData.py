from peewee import *
from BaseModel import *
from misc_functions import *
from NamedModel import NamedModel

class ItemTypeData(NamedModel):

    def to_string(self):
        return str(self.name)

    def get_by_name(name):
        try:
            obj = ItemTypeData.select().where(fn.Lower(ItemTypeData.name) == fn.Lower(name))
        except ItemTypeData.DoesNotExist:
            obj = None

        return obj