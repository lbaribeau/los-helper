from peewee import *
from db.BaseModel import *
from db.Mob import *
from misc_functions import *

class MobMessage(BaseModel):
    mob = ForeignKeyField(Mob)
    keyword = CharField(null=True)
    message = CharField(null=True)

    def map(self):
        is_new_mapping = False
        mobMessage = MobMessage.get_message_by_mob_and_keyword(self.mob, self.keyword)

        if mobMessage is None:
            super(MobMessage, self).save()
            is_new_mapping = True
        else:
            if self.message != mobMessage.message:
                super(MobMessage, self).save()
                is_new_mapping = True

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + str(self.keyword) + ", " + str(self.message) + ", " + str(self.mob)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def get_message_by_keyword(mob, keyword):
        try:
            mobMessage = MobMessage.select().where((MobMessage.mob.id == mob.id) & (MobMessage.keyword == keyword)).get()
        except MobMessage.DoesNotExist:
            mobMessage = None

        return mobMessage