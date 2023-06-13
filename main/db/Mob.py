
from peewee import *
from db.BaseModel import *

from misc_functions import *
from db.NamedModel import NamedModel

class Mob(NamedModel):
    description       = CharField(null=True)
    level             = IntegerField(null=True)
    approximate_level = IntegerField(null=True)
    difficulty_rating = IntegerField(null=True)
    aura = IntegerField(null=True)
    is_hostile = BooleanField(default=False)
    blocks_exit = BooleanField(default=False)
    blocks_pickup = BooleanField(default=False)
    is_named = BooleanField(default=False)
    should_farm = BooleanField(default=False)
    # health = IntegerField(default=0)
    # approximate_health = IntegerField(default=0)
    uses_black_magic = BooleanField(default=False) # uses damage spells
    uses_white_magic = BooleanField(default=False) # heals itself
    uses_grey_magic = BooleanField(default=False) # uses things like stun/confuse/blind
    uses_ability = BooleanField(default=False) # uses an ability that isn't a particular spell (typically AOE effect)
    is_magical = BooleanField(default=False) # can only be hit with magical weapons
    is_undead = BooleanField(default=False) # can't be hit with certain abilities, can be turned
    deflects_attacks = BooleanField(default=False) # reduces damage from physical attacks by a lot
    joins_in = BooleanField(default=False) # joins in on fights
    flees = BooleanField(default=False) # flees from fights
    element = IntegerField(default=0) # tbd future column
    note = CharField(null=True)

    '''Private Mob Functions'''
    def map(self):
        is_new_mapping = False
        mob = Mob.get_mob_by_name(self.name)

        if mob is None:
            is_new_mapping = True
            super(Mob, self).save()
        else:
            self.id                = mob.id
            self.blocks_pickup     = mob.blocks_pickup
            self.blocks_exit       = mob.blocks_exit
            self.level             = mob.level
            self.approximate_level = mob.approximate_level
            self.aura = mob.aura
            # self.health = mob.health
            # self.approximate_health = mob.approximate_health

        return is_new_mapping

    def to_string(self):
        #return 'ID: '+str(self.id) + ", " + str(self.name) + ", " + str(self.level) + ", " + str(self.aura)
        return 'ID: {0}\nName: {1}\nLevel: {2}\nAura: {3}\n'.format(self.id, self.name, self.level, self.aura)

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
                        ((level + coalesce(difficulty_rating, 0)) between {0} and {1} or ((level + coalesce(difficulty_rating, 0)) < {1} and should_farm = 1))
                        and  (aura between {2} and {3})""".format(
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