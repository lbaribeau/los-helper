from peewee import *

from db.NamedModel import NamedModel
from db.BaseModel import *
from misc_functions import *

class ItemTypeModel(NamedModel):

    def to_string(self):
        return str(self.name)

    def get_by_name(name):
        try:
            obj = ItemTypeModel.select().where(fn.Lower(ItemTypeModel.name) == fn.Lower(name))
        except ItemTypeModel.DoesNotExist:
            obj = None

        return obj