from peewee import *
from Database import *
from misc_functions import *
from GenericMudObject import *

class MudMob(GenericMudObject):
    is_unusable = False

    def __init__(self, name):
        self.obj = Mob(name=name)
        self.item = self.obj
        self.reference = get_last_word(self.obj.name)

    def map(self):
        self.obj.map()

    def get_location(self):
        return MobLocation.get_locations_by_mob_id(self.obj.id)

    ''' Static Functions '''
    def get_mobs_by_level_and_aura(level, aura):
        return MobLocation.get_locations_by_mobs_level_and_aura(level, aura)

    ''' Static Functions '''
    def get_mobs_by_level_and_aura_ranges(low_level, high_level, low_aura, high_aura):
        return MobLocation.get_locations_by_mob_level_range_and_aura_range(low_level, high_level, low_aura, high_aura)