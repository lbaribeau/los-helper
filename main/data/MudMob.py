from peewee import *
from Database import *
from misc_functions import *
from GenericMudObject import *

class MudMob(GenericMudObject):
    is_unusable = False
    item = None

    def __init__(self, name):
        self.obj = Mob(name=name)
        self.item = self.obj
        self.reference = get_last_word(self.obj.name)

    def map(self):
        self.obj.map()