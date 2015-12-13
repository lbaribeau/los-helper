from peewee import *
from db.Database import *
from db.NamedModel import NamedModel
from misc_functions import *

class GenericMudObject(object):
    # def __init__(self, name=None):
    def __init__(self):
        self.obj = None
        self.reference = None
        self.conserve = False

        # if name:
        #     self.obj = object()
        #     self.obj.name = name

    def map(self):
        raise NotImplementedError()

    @property
    def name(self):
        return self.obj.name

    @property
    def is_usable(self):
        return self.obj.is_usable

    def to_string(self):
        return self.name

    def __getitem__(self, key):
        return NamedModel.get_by_name(key)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
        if isinstance(other, 'str'.__class__):
            return self.name == other
        else:
            return self.name == other.name

    def __lt__(self, other):
        if isinstance(other, 'str'.__class__):
            return self.name < other
        else:
            return self.name < other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # return 0
        return self.obj.id

