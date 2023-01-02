
#import peewee
from db.NamedModel import NamedModel
#from misc_functions import *

# "TypeData" is more specific than model (weapon/armour/item)
# It's what kind of weapon, or where the armour is worn
# The item type table is a merger of these two tables

# +----+---------+
# | id | name    |
# +----+---------+
# |  1 | Sharp   |
# |  2 | Thrust  |
# |  3 | Blunt   |
# |  4 | Pole    |
# |  5 | Missile |
# |  6 | Body    |
# |  7 | Arms    |
# |  8 | Legs    |
# |  9 | Neck    |
# | 10 | Hands   |
# | 11 | Head    |
# | 12 | Feet    |
# | 13 | Finger  |
# | 14 | Shield  |
# | 15 | Face    | (new)
# +----+---------+

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

        #print('ItemTypeData get_by_name(name) returning: ' + str(obj))
        #NamedModel.magentaprint('ItemTypeData get_by_name(name) returning: ' + str([o.name for o in obj]))
        return obj