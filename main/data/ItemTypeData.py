from peewee import *
from BaseModel import *
from misc_functions import *
from NamedModel import NamedModel

class ItemTypeData(NamedModel):

    def to_string(self):
        return str(self.name)