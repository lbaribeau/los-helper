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
