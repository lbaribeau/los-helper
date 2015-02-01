from peewee import *
from BaseModel import *
from misc_functions import *
from NamedModel import NamedModel

class ItemTypeModel(NamedModel):

    def to_string(self):
        return str(self.name)