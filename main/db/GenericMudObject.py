from peewee import *
from db.Database import *
from db.NamedModel import NamedModel
from misc_functions import *

class GenericMudObject():
    obj = None
    reference = None
    conserve = False

    def map(self):
        raise NotImplementedError()

    def to_string(self):
        return self.obj.name

    def __getitem__(self,key):
        return NamedModel.get_by_name(key)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
        is_equal = isinstance(other, self.__class__)

        if is_equal:
            is_equal = self.obj.name == other.obj.name

        return is_equal

    def __lt__(self, other):
        return self.obj.name < other.obj.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.obj.id