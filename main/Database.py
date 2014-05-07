'''In order for this class to work you need to have installed Peewee
See: http://peewee.readthedocs.org/en/latest/peewee/installation.html
'''
from peewee import *
from misc_functions import *
import time
from datetime import datetime

db = Proxy()

class BaseModel(Model):
    def __eq__(self, other): #simple type check
        if type(other) is type(self):
            return True
        else:
            return False

    class Meta:
        database = db

class Area(BaseModel):
    name = CharField() #Chapel
    description = CharField(null=True) #This will only be used for crawler comparisons
    is_always_dark = BooleanField(default=False)
    is_dark_at_night = BooleanField(default=False)
    is_restorative = BooleanField(default=False)

    '''Private Area Functions'''
    def map(self, exits, cur_area_from=None, cur_exit_from=None):
        is_new_mapping = True

        mapped_exits = []
        for exit in exits:
            exit.map() # this will update our exit objects with their corresponding ids
            mapped_exits.append(exit)

        is_new_mapping = self.search_for_area(mapped_exits)

        #if (cur_area_from is None):
            
        #elif (cur_area_from.name != self.name): #if the names are the same then this is a new area since we have moved
        #    is_new_mapping = self.search_for_area(mapped_exits)

        if is_new_mapping: #this means the search has found the matching area and our Area.ID is set
            super(Area, self).save()

            #now we map our area exits
            for exit in mapped_exits:
                #magentaprint("exit " + str(exit.to_string()), False)
                area_exit = AreaExit(area_from=self.id, area_to=None, exit_type=exit)

                '''if (exit_from.opposite is None):
                    if (exit.id == exit_from.opposite.id):
                        area_exit.map(area_from, exit_from)
                    else:'''

                area_exit.map()

        #last but not least we want to try to update our area_from with it's area_to value :)
        if cur_area_from is not None and cur_exit_from is not None:
            area_exit_from = AreaExit.get_area_exit_by_area_from_and_exit_type(cur_area_from, cur_exit_from)
            if (area_exit_from is not None):
                if (area_exit_from.area_to is None): #don't overwrite values that have been
                    area_exit_from.area_to = self
                    area_exit_from.save()
                    magentaprint("Updating AreaExit with: \n" + area_exit_from.to_string())

        return is_new_mapping

    def search_for_area(self, mapped_exits):
        is_new_mapping = True
        matching_areas = Area.get_areas_by_name_and_description(self.name, self.description)
        for area in matching_areas: #we selected based on name / description so we know they match but just in case or if our descriptions are null
            if (area.has_exits(mapped_exits)):
                self.id = area.id
                is_new_mapping = False
                return is_new_mapping #we want to stop the search if we've found a match

        return is_new_mapping

    def has_exits(self, exits): #receiving mapped exits with IDs so we just do a compare on the Area Links
        area_exits = AreaExit.get_area_exits_from_area(self)
        has_exits = (area_exits.count() == len(exits))

        if (has_exits): #if the number of exits we have is the same
            exit_found = False
            for exit_type in exits:
                exit_found = False
                for area_exit in area_exits:
                    if (exit_type.id == area_exit.exit_type.id or area_exit.is_hidden):
                        exit_found = True
                if not exit_found:
                    return False
            has_exits = exit_found

        return has_exits

    def to_string(self):
        return str(self.id) + ", " + self.name + ", " + str(self.description)

    '''Static Area Functions'''
    def get_areas_by_name_and_description(area_name, area_description):
        areas = []

        try:
            areas = Area.select().where((Area.name == area_name) & (Area.description == area_description))

        except Area.DoesNotExist:
            areas = []

        return areas

    def get_area_by_id(area_id):
        area = []

        try:
            area = Area.select().where(Area.id == area_id).get()
        except Area.DoesNotExist:
            area = None

        return area

    def get_areas_by_partial_name(area_name_part):
        areas = []

        area_name = "*" + area_name_part + "*"

        try:
            areas = Area.select().where((Area.name % area_name))

        except Area.DoesNotExist:
            areas = []

        return areas


class ExitType(BaseModel):
    name = CharField() #ex. north, out, door

    '''Private Area Functions'''
    def map(self):
        is_new_mapping = False

        exit_type = ExitType.get_exit_type_by_name(self.name)

        if (exit_type is None): #in this case we've discovered a new exit
            super(ExitType, self).save()
            is_new_mapping = True
            return is_new_mapping
        else:
            self.id = exit_type.id

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + self.name

    '''Static ExitType Functions'''
    def get_exit_type_by_name(name): #this should always be unique
        exit_types = None

        try:
            exit_types = ExitType.select().where((ExitType.name == name)).get()
        except ExitType.DoesNotExist:
            #magentaprint("Could not find exit Type with name: " + name, False)
            exit_types = None

        return exit_types

    def get_exit_type_by_name_or_shorthand(name):
        exit_types = None

        try:
            #magentaprint("matching exit to: " + str(name))
            exit_types = ExitType.select().join(ExitSynonym, JOIN_LEFT_OUTER).where((ExitType.name == name) | (ExitSynonym.name == name) ).get()
            #magentaprint("matched exit to: " + exit_types.to_string())
        except ExitType.DoesNotExist:
            #magentaprint("Could not find exit Type with name: " + name, False)
            exit_types = None

        return exit_types

    def get_exit_type_by_name_and_opposite(name, exit_id): #this should always be unique
        exit_types = None

        try:
            exit_types = ExitType.select().join(ExitOpposite).where((ExitType.name == name) & (ExitOpposite.exit.name == name)).get()

        except ExitType.DoesNotExist:
            exit_types = None

        return exit_types

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
        return str(self.id) + ", " + str(self.area_from.name) + ", " + str(self.get_area_to_name()) + ", " + str(self.exit_type.name)

    '''Static AreaExit Functions'''
    def get_area_exit_by_area_from_and_exit_type(cur_area_from, cur_exit_type):
        try:
            area_exit = AreaExit.select().where((AreaExit.area_from == cur_area_from.id) & (AreaExit.exit_type == cur_exit_type.id)).get()
        except AreaExit.DoesNotExist:
            area_exit = None

        return area_exit

    def get_area_exits_from_area(area):
        try:
            area_exits = AreaExit.select().where((AreaExit.area_from == area.id))
        except AreaExit.DoesNotExist:
            area_exits = []

        return area_exits

class ExitOpposite(BaseModel):
    exit = ForeignKeyField(ExitType, related_name='exit_to')
    opposite = ForeignKeyField(ExitType, related_name='exit_from')

class ExitSynonym(BaseModel):
    name = CharField()
    exit = ForeignKeyField(ExitType, null=True)

class Mob(BaseModel):
    name = CharField()
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

class Log(BaseModel):
    timestamp = DateTimeField(default=datetime.now)
    data = TextField()

    def to_string(self):
        return str(self.timestamp) + ", " + str(self.data)

def create_tables():
    try:
        Log.create_table()
        Area.create_table()
        AreaExit.create_table()
        ExitType.create_table()
        ExitOpposite.create_table()
        ExitSynonym.create_table()
        Mob.create_table()
        MobLocation.create_table()
    except:
        pass

def drop_tables():
    try:
        Log.drop_table()
        Area.drop_table()
        AreaExit.drop_table()
        ExitType.drop_table()
        ExitOpposite.drop_table()
        ExitSynonym.drop_table()
        Mob.drop_table()
        MobLocation.drop_table()
    except:
        pass