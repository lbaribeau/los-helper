from peewee import *
from BaseModel import *
from misc_functions import *

class ItemType(BaseModel):
    model = ForeignKeyField(ItemTypeModel, null=True)
    data = ForeignKeyField(ItemDataModel, null=True)
    note = CharField(null=True)

    def to_string(self):
        return str(self.id) + ", " + str(self.data)