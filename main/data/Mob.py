from peewee import *
from BaseModel import *
from misc_functions import *

class Mob(BaseModel):
    name = CharField()
    description = CharField(null=True)
    level = IntegerField(null=True)
    approximate_level = IntegerField(null=True)
    difficulty_rating = IntegerField(null=True)
    aura = IntegerField(null=True)
    is_hostile = BooleanField(default=False)
    blocks_exit = BooleanField(default=False)
    blocks_pickup = BooleanField(default=False)

    '''Private Mob Functions'''
    def map(self):
        is_new_mapping = False
        mob = Mob.get_mob_by_name(self.name)

        if mob is None:
            super(Mob, self).save()
        else:
            self.id = mob.id
            self.blocks_pickup = mob.blocks_pickup
            self.blocks_exit = mob.blocks_exit
            self.level = mob.level
            self.approximate_level = mob.approximate_level
            self.aura = mob.aura
            #update other fields if you want

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + str(self.name) + ", " + str(self.level)

    '''Static Mob Functions'''
    def get_mob_by_name(name):
        try:
            mob = Mob.select().where((Mob.name == name)).get()
        except Mob.DoesNotExist:
            mob = None

        return mob