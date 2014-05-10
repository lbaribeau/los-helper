from peewee import *
from BaseModel import *
from misc_functions import *
from Area import *
from Mob import *

class MobLocation(BaseModel):
    area = ForeignKeyField(Area)
    mob = ForeignKeyField(Mob)

    '''Private Mob Functions'''
    def map(self):
        is_new_mapping = False
        mob_locations = MobLocation.is_mob_in_area(self.mob.id, self.area.id)

        if mob_locations is None:
            super(MobLocation, self).save()
        else:
            self.id = mob_locations.id
            #update other fields if you want

        return is_new_mapping

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