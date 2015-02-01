from peewee import *
from misc_functions import *
from Database import *
from BaseModel import BaseModel

class NamedModel(BaseModel):
    name = CharField() #Chapel

    '''Static Item Functions'''
    def get_by_name(name):
        try:
            obj = NamedModel.select().where((NamedModel.name == name)).get()
        except NamedModel.DoesNotExist:
            obj = None

        return obj