
from peewee import *

from db.BaseModel import *
from db.Area import *
from db.Mob import *
from misc_functions import *

class MobLocation(BaseModel):
    area = ForeignKeyField(Area)
    mob = ForeignKeyField(Mob)
    sightings = IntegerField(default=1)
    # rank = FloatField(default=0)

    '''Private Mob Functions'''
    def map(self):
        is_new_mapping = False
        mob_locations = MobLocation.is_mob_in_area(self.mob.id, self.area.id)

        if mob_locations is None:
            is_new_mapping = True
            super(MobLocation, self).save()
        else:
            self.id   = mob_locations.id
            self.area = mob_locations.area
            self.mob = mob_locations.mob
            self.sightings = mob_locations.sightings
            # self.rank = mob_locations.rank
            #update other fields if you want

        return is_new_mapping

    def increment_sightings(self):
        # print("increment_sightings {}".format(self.sightings))
        self.sightings += 1
        super(MobLocation, self).save()

    def to_string(self):
        return str(self.id) + ", " + str(self.area.name) + ", " + str(self.mob.name)

    '''Static Mob Functions'''
    def is_mob_in_area(mob_id, area_id):
        try:
            mob_locations = MobLocation.select().where((MobLocation.area == area_id) & (MobLocation.mob == mob_id)).get()
        except MobLocation.DoesNotExist:
            mob_locations = None
        return mob_locations

    def get_locations_by_partial_mob_name(mob_name_part):
        mob_locations = []
        mob_name = "*" + mob_name_part + "*"
        try:
            mob_locations = MobLocation.select().join(Mob).where(Mob.name % mob_name).order_by(Mob.id.desc())
        except MobLocation.DoesNotExist:
            mob_locations = []
        return mob_locations

    def get_locations_by_exact_mob_name(mob_name):
        mob_locations = []
        try:
            mob_locations = MobLocation.select().join(Mob).where(Mob.name == mob_name).order_by(Mob.id.desc())
        except MobLocation.DoesNotExist:
            mob_locations = []
        return mob_locations

    def get_locations_by_mob_id(id):
        mob_locations = []
        try:
            mob_locations = MobLocation.select().join(Mob).where(Mob.id == id).order_by(Mob.id.desc())
        except MobLocation.DoesNotExist:
            mob_locations = []
        return mob_locations

    def get_locations_by_mobs_level(level):
        try:
            mob_locations = MobLocation.select().join(Mob).where(Mob.level == level)
        except Mob.DoesNotExist:
            mob_locations = []
        return mob_locations

    def get_locations_by_mobs_level_and_aura(level, aura):
        try:
            mob_locations = MobLocation.select().join(Mob).where((Mob.level == level) & (Mob.aura == aura))
        except Mob.DoesNotExist:
            mob_locations = []
        return mob_locations

    def get_locations_by_mob_level_range_and_aura_range(low_level, high_level, low_aura, high_aura):
        try:
            mob_locations = MobLocation.select().join(Mob).where((Mob.level.between(low_level, high_level)) &
                 (Mob.aura.between(low_aura, high_aura)) &
                 ~(Mob.name.contains("guard"))).order_by(Mob.level.asc())
        except Mob.DoesNotExist:
            mob_locations = []
        return mob_locations
