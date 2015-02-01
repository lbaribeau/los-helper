from peewee import *
from BaseModel import *
from misc_functions import *
from ItemTypeModel import *
from ItemTypeData import *

class ItemType(BaseModel):
    model = ForeignKeyField(ItemTypeModel, null=True)
    data = ForeignKeyField(ItemTypeData, null=True)
    note = CharField(null=True)

    def to_string(self):
        return str(self.model) + ", " + str(self.data)