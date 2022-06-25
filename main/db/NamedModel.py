
import peewee

from misc_functions import *
from db.Database import *
import db.BaseModel

class NamedModel(db.BaseModel.BaseModel):
    name = peewee.CharField() #Chapel

    '''Static Item Functions'''
    def get_by_name(name):
        try:
            obj = NamedModel.select().where(peewee.fn.Lower(NamedModel.name) == peewee.fn.Lower(name)).get()
        except NamedModel.DoesNotExist:
            obj = None

        return obj

# peewee.OperationalError: no such table: namedmodel
# So I don't think this is getting inherted very well, at least not Area.get_by_name()
# Why not be case sensitive
