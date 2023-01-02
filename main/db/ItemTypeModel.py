from peewee import *

from db.NamedModel import NamedModel
from db.BaseModel import *
from misc_functions import *

# Item "models"
# ie what kind of item is it (weapon, consumable, size of armour, reageant, scroll, etc.)
# +----+------------+ 
# | id | name       |
# +----+------------+
# |  1 | weapon     |
# |  2 | s-armor    |
# |  3 | m-armor    |
# |  4 | l-armor    |
# |  5 | consumable |
# |  6 | held       |
# |  7 | reageant   |
# |  8 | scroll     |
# |  9 | quest      |
# | 10 | trash      |
# | 11 | armor      |
# +----+------------+

class ItemTypeModel(NamedModel):
    def to_string(self):
        return str(self.name)

    def get_by_name(name):
        # print("ItemTypeModel.get_by_name() name: " + str(name))
        # print("ItemTypeModel.get_by_name() ItemTypeModel.name: " + str(ItemTypeModel.name))
        # print("ItemTypeModel fn: " + str(fn))
        # print("ItemTypeModel obj: " + ItemTypeModel.select().where(ItemTypeModel.name == name))
        try:
            obj = ItemTypeModel.select().where(fn.Lower(ItemTypeModel.name) == fn.Lower(name))
            # obj = ItemTypeModel.select().where(ItemTypeModel.name == name)
        except ItemTypeModel.DoesNotExist:
            print("ItemTypeModel exception!")
            obj = None

        return obj