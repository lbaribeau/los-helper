from peewee import *
from misc_functions import *
from Database import *

class BaseModel(Model):
    def __eq__(self, other): #simple type check
        if type(other) is type(self):
            return True
        else:
            return False

    class Meta:
        database = db

    def to_string(self):
        return str(self.id)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    '''Static BaseModel Functions'''
    def get_by_id(id):
        try:
            obj = BaseModel.select().where((BaseModel.id == id)).get()
        except BaseModel.DoesNotExist:
            obj = None

        return obj
