from peewee import *
from db.BaseModel import *
from misc_functions import *
from db.NamedModel import NamedModel

class Mob(NamedModel):
    description = CharField(null=True)
    level = IntegerField(null=True)
    approximate_level = IntegerField(null=True)
    difficulty_rating = IntegerField(null=True)
    aura = IntegerField(null=True)
    is_hostile = BooleanField(default=False)
    blocks_exit = BooleanField(default=False)
    blocks_pickup = BooleanField(default=False)
    is_named = BooleanField(default=False)

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
        return str(self.id) + ", " + str(self.name) + ", " + str(self.level) + ", " + str(self.aura)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    '''Static Mob Functions'''
    def get_mob_by_name(name):
        try:
            mob = Mob.select().where((Mob.name == name)).get()
        except Mob.DoesNotExist:
            mob = None

        return mob

    def get_mobs_by_partial_name(name):
        try:
            partial_name = "*" + name + "*"
            mobs = Mob.select().where(Mob.name % partial_name).order_by(Mob.id.desc())
        except Mob.DoesNotExist:
            mobs = []

        return mobs

    def get_mobs_by_level_and_aura_ranges(low_level, high_level, low_aura, high_aura):

        try:

            sql = """SELECT *
                     FROM MOB
                     Where 
                        (level between {0} and {1} or (level <= {1} and difficulty_rating = 1))
                        and  (aura between {2} and {3})
                        and (difficulty_rating is null or difficulty_rating != 2)""".format(
                            low_level, high_level, low_aura, high_aura)
            # print(sql)

            mobs = Mob.raw(sql)
            # mobs = Mob.select().where(
            #         (
            #             (
            #                 Mob.level.between(low_level, high_level) |
            #                 Mob.difficulty_rating == 1 & Mob.level <= high_level
            #             )
            #         ) &
            #         (
            #             Mob.aura.between(low_aura, high_aura)
            #         )
                    # &
                    # (
                    #     (Mob.difficulty_rating != 2 | Mob.difficulty_rating.is_null(True))
                    # )
                # )
        except Mob.DoesNotExist:
            mobs = []

        return mobs