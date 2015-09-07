from peewee import *
from db.BaseModel import *
from misc_functions import *
from db.Area import *
from db.ExitType import *

class AreaExit(BaseModel):
    area_from = ForeignKeyField(Area, related_name='area_from') #id is a default attribute
    area_to = ForeignKeyField(Area, related_name='area_to', null=True) #id is a default attribute
    exit_type = ForeignKeyField(ExitType)
    is_useable = BooleanField(default=True) #if the link is broken or potentially harzardous we don't want to use it
    is_hidden = BooleanField(default=False) #these will be manually set for now
    note = CharField(default="")

    '''Private Area Functions'''
    def map(self, area_from=None, exit_from=None):
        is_new_mapping = False

        if area_from is not None and exit_from is not None:
            if exit_from.opposite is not None:
                if self.exit_type.id == exit_from.opposite.id:
                    area_exit.area_to = area_from
            #else:
                '''code a case to handle this exit issue on opposites (west opposite out)
                since most of the exit types are likely going to have hardcoded opposite at first
                and then especially for exceptions like this it might not be worth the effort
                A github issue will be made'''

        super(AreaExit, self).save()

        return is_new_mapping

    def get_area_to_name(self):
        if (self.area_to is not None):
            return self.area_to.name
        else:
            return None

    def to_string(self):
        return "<id: " + str(self.id) + ", from-name:" + str(self.area_from.name) + ", to-name:" + str(self.get_area_to_name()) + ", exit-name:" + str(self.exit_type.name) + ">"

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    '''Static AreaExit Functions'''
    def get_area_exit_by_area_from_and_exit_type(cur_area_from, cur_exit_type):
        area_exit = None

        try:
            for ae in AreaExit.select().where((AreaExit.area_from == cur_area_from.id) & (AreaExit.exit_type == cur_exit_type.id)):
                area_exit = ae
                break
        except AreaExit.DoesNotExist:
            area_exit = None

        return area_exit

    def get_area_exits_from_area(area):
        area_exits = []
        try:
            for ae in AreaExit.select().where((AreaExit.area_from == area.id)):
                area_exits.append(ae)
        except AreaExit.DoesNotExist:
            area_exits = []

        return area_exits