from peewee import *
from db.Database import *
from misc_functions import *
from db.GenericMudObject import *

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
    def get_mobs_by_level_and_aura_ranges(low_level, high_level, low_aura, high_aura):
        return Mob.get_mobs_by_level_and_aura_ranges(low_level, high_level, low_aura, high_aura)

    def get_areas_to_mob(area_id, mob_name):
        area_ids = []

        try:
            mob_locations = MobLocation.select().join(Mob).where((Mob.name == mob_name) &
             (MobLocation.area.id == area_id)).order_by(Mob.id.desc())

            for location in mob_locations:
                area_ids += location.area.id

        except MobLocation.DoesNotExist:
            mob_locations = []

        return area_ids