from peewee import *
from db.BaseModel import *
from misc_functions import *
from db.Mob import *
from db.Item import *

class MobLoot(BaseModel):
    mob = ForeignKeyField(Mob, related_name='mod_id')
    item = ForeignKeyField(Item, related_name='item_id')

    def map(self):
        is_new_mapping = False
        mob_item = MobLoot.get_by_mob_and_item(self.mob.id, self.item.id)

        if mob_item is None:
            is_new_mapping = True
            super(MobLoot, self).save()
        else:
            self.id = mob_item.id
            self.mob = mob_item.mob
            self.item = mob_item.item
        
        return is_new_mapping
    
    def get_by_mob_and_item(mob_id, item_id):
        mob_item = None
        try:
            mob_item = MobLoot.select().where((MobLoot.mob == mob_id) & (MobLoot.item == item_id)).get()
        except MobLoot.DoesNotExist:
            mob_item = None

        return mob_item