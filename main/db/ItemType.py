from peewee import *
from db.BaseModel import *
from db.ItemTypeModel import *
from db.ItemTypeData import *
from misc_functions import *

# id|model_id|data_id|note          |
# --+--------+-------+--------------+
#  1|       1|      1|Sharp Weapon  |
#  2|       1|      2|Thrust Weapon |
#  3|       1|      3|Blunt Weapon  |
#  4|       1|      4|Pole Weapon   |
#  5|       1|      5|Missile Weapon|
#  6|       2|      6|Body (s)      |
#  7|       2|      7|Arms          |
#  8|       2|      8|Legs          |
#  9|       2|      9|Neck          |
# 10|       2|     10|Hands         |
# 11|       2|     11|Head          |
# 12|       2|     12|Feet          |
# 13|      11|     13|Finger        |
# 14|      11|     14|Shield        |
# 15|       3|      6|Body (m)      |
# 16|       3|      7|Arms          |
# 17|       3|      8|Legs          |
# 18|       3|      9|Neck          |
# 19|       3|     10|Hands         |
# 20|       3|     11|Head          |
# 21|       3|     12|Feet          |
# 24|       4|      6|Body (l)      |
# 25|       4|      7|Arms          |
# 26|       4|      8|Legs          |
# 27|       4|      9|Neck          |
# 28|       4|     10|Hands         |
# 29|       4|     11|Head          |
# 30|       4|     12|Feet          |
# 31|      11|      6|Body (unsized)|
# 32|      11|      7|Arms          |
# 33|      11|      8|Legs          |
# 34|      11|      9|Neck          |
# 35|      11|     10|Hands         |
# 36|      11|     11|Head          |
# 37|      11|     12|Feet          |

class ItemType(BaseModel):
    model = ForeignKeyField(ItemTypeModel, null=True)
    data = ForeignKeyField(ItemTypeData, null=True)
    note = CharField(null=True)

    def to_string(self):
        return str(self.model) + ", " + str(self.data)

    def has_model_and_data(self, model_name, data_name):
        print("ItemType.has_model_and_data() model_name: " + str(model_name) + ", data_name: " + str(data_name))
        is_of_type = False

        if self.model is not None:
            if self.model.name.lower() == model_name.lower():
                if self.data is not None:
                    if self.data.name.lower() == data_name.lower():
                        is_of_type = True


        return is_of_type
