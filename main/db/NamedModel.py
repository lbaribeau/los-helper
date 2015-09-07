from peewee import *
from misc_functions import *
from db.Database import *
from db.BaseModel import BaseModel

class NamedModel(BaseModel):
    name = CharField() #Chapel

    '''Static Item Functions'''
    def get_by_name(name):
        try:
            obj = NamedModel.select().where(fn.Lower(NamedModel.name) == fn.Lower(name)).get()
        except NamedModel.DoesNotExist:
            obj = None

        return obj