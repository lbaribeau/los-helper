from peewee import *
from db.BaseModel import *
from db.ItemTypeModel import *
from db.ItemTypeData import *
from misc_functions import *

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
