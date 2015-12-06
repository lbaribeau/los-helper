from peewee import *
from db.Database import *
from db.NamedModel import NamedModel
from misc_functions import *

class GenericMudList():
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

    def __len__(self):
        return self.qty

    # Why are we using this and not a built in list []
    def __iter__(self):
        self.current_iter = 0
        return iter(self.objs)

    def __next__(self):
        if self.current_iter > self.qty:
            raise StopIteration
        else:
            self.current_iter += 1
            return self.objs[self.current_iter - 1]