'''In order for this class to work you need to have installed Peewee
See: http://peewee.readthedocs.org/en/latest/peewee/installation.html
'''
from peewee import *
from misc_functions import *

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
    def map(self, directions, area_from=None, direction_from=None):
        is_new_mapping = False

        mapped_directions = []

        for direction in directions:
            direction.map() # this will update our direction objects with their corresponding ids
            mapped_directions.append(direction)

        matching_areas = Area.get_areas_by_name_and_description(self.name, self.description)

        for area in matching_areas: #we selected based on name / description so we know they match but just in case or if our descriptions are null
            if (area.has_directions(mapped_directions)):
                self.id = area.id
                return is_new_mapping

        is_new_mapping = True
        super(Area, self).save()

        #now we map our area links
        for direction in mapped_directions:
            #magentaprint("Direction " + str(direction.to_string()), False)
            area_link = AreaLink(area_from=self.id, area_to=None, direction_type=direction)

            '''if (direction_from.opposite is None):
                if (direction.id == direction_from.opposite.id):
                    area_link.map(area_from, direction_from)
                else:'''

            area_link.map()

        return is_new_mapping

    def has_directions(self, directions): #receiving mapped directions with IDs so we just do a compare on the Area Links
        area_links = AreaLink.get_area_links_from_area(self)
        has_directions = (area_links.count() == len(directions))

        #print("has_directions: " + str(has_directions) + " area: " + str(area.to_string()))

        if (has_directions):
            direction_found = False
            for direction_type in directions:
                direction_found = False
                for area_link in area_links:
                    if (direction_type == area_link.direction_type):
                        direction_found = True
                if not direction_found:
                    return False
            has_directions = direction_found

        return has_directions

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

class DirectionType(BaseModel):
    name = CharField() #ex. north, out, door
    shorthand = CharField(null=True) #user input alternative North == n
    primer = CharField(null=True) #ex. open %s, unlock %s key
    opposite = ForeignKeyField('self', null=True)

    '''Private Area Functions'''
    def map(self):
        is_new_mapping = False
        direction_type = None

        if (self.opposite is None):
            direction_type = DirectionType.get_direction_type_by_name(self.name)
        else: 
            direction_type = DirectionType.get_direction_type_by_name_and_opposite(self.name, self.opposite)

        if (direction_type is None): #in this case we've discovered a new direction
            super(DirectionType, self).save()
            direction_type = self
            is_new_mapping = True
            return is_new_mapping
        else:
            self.id = direction_type.id
            self.shorthand = direction_type.shorthand
            self.primer = direction_type.primer
            self.opposite = direction_type.opposite

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + self.name + ", " + str(self.primer) + ", " + str(self.opposite)

    '''Static DirectionType Functions'''
    def get_direction_type_by_name(name): #this should always be unique
        direction_types = None

        try:
            direction_types = DirectionType.select().where((DirectionType.name == name)).get()
        except DirectionType.DoesNotExist:
            #magentaprint("Could not find Direction Type with name: " + name, False)
            direction_types = None

        return direction_types

    def get_direction_type_by_name_and_opposite(name, direction_id): #this should always be unique
        direction_types = None

        try:
            direction_types = DirectionType.select().where((DirectionType.name == name) &
             (DirectionType.opposite == direction_id)).get()

        except DirectionType.DoesNotExist:
            direction_types = None

        return direction_types

class AreaLink(BaseModel):
    area_from = ForeignKeyField(Area, related_name='area_from') #id is a default attribute
    area_to = ForeignKeyField(Area, related_name='area_to', null=True) #id is a default attribute
    direction_type = ForeignKeyField(DirectionType)
    is_useable = BooleanField(default=True) #if the link is broken or potentially harzardous we don't want to use it

    '''Private Area Functions'''
    def map(self, area_from=None, direction_from=None):
        is_new_mapping = False

        if area_from is not None and direction_from is not None:
            if self.direction_type == direction_from.opposite:
                area_link.area_to = area_from
            else:
                '''code a case to handle this direction issue on opposites (west opposite out)
                since most of the direction types are likely going to have hardcoded opposite at first
                and then especially for exceptions like this it might not be worth the effort
                A github issue will be made'''

        super(AreaLink, self).save()

        return is_new_mapping

    def get_area_to_name(self):
        if (self.area_to is not None):
            return self.area_to.name
        else:
            return None

    def to_string(self):
        return str(self.id) + ", " + str(self.area_from.name) + ", " + str(self.get_area_to_name()) + ", " + str(self.direction_type.name)

    '''Static AreaLink Functions'''
    def get_area_links_from_area(area):
        try:
            area_links = AreaLink.select().where((AreaLink.area_from == area.id))
        except AreaLink.DoesNotExist:
            area_links = []

        return area_links

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
        return

    def to_string(self):
        return str(self.id) + ", " + str(self.name) + ", " + str(self.level)

    '''Static Mob Functions'''

class AreaMobs(BaseModel):
    area = ForeignKeyField(Area)
    mob = ForeignKeyField(Mob)

    '''Private Mob Functions'''
    def map(self):
        return

    def to_string(self):
        return str(self.id) + ", " + str(self.area.name) + ", " + str(self.mob.name)

    '''Static Mob Functions'''

def create_tables():
    try:
        Area.create_table()
        AreaLink.create_table()
        DirectionType.create_table()
        #Mob.create_table()
    except:
        pass

def drop_tables():
    try:
        Area.drop_table()
        AreaLink.drop_table()
        DirectionType.drop_table()
        #Mob.drop_table()
    except:
        pass