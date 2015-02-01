from peewee import *
from Database import *
from misc_functions import *
from NamedModel import NamedModel

class GenericMudList():
    objs = []
    qty = 1

    def __init__(self, objs):
        self.objs = objs
        self.set_quantity()

    def add(self, obj_list):
        self.objs += obj_list.objs
        self.set_quantity()

    def remove(self, index=0):
        self.objs.pop(index)
        self.set_quantity()

    def set_quantity(self):
        self.qty = len(self.objs)        

    def to_string(self):
        return str(self.qty)

    def __int__(self):
        return self.qty

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()