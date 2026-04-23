from peewee import *
from db.BaseModel import *
from misc_functions import *
from db.Area import *
from db.ExitType import *

class AreaExit(BaseModel):
    """ 
        Has:
            exit_type : ie. 
                id: 7, 
                name: northeast
            area_from <Area> # A MudArea??? No just an AREA
            area_to   <Area>
            is_useable <Boolean>
            is_hidden <Boolean>
            note <string>
    """
    area_from  = ForeignKeyField(Area, related_name='area_from') #id is a default attribute ie. "431, The South Plains Road"
    area_to    = ForeignKeyField(Area, related_name='area_to', null=True) #id is a default attribute... ie. "430, The South Plains Road"
    exit_type  = ForeignKeyField(ExitType)  # ie. "17, northeast"
    is_useable = BooleanField(default=True) #if the link is broken or potentially harzardous we don't want to use it
    is_hidden  = BooleanField(default=False) #these will be manually set for now
    note       = CharField(default="")

    '''Private Area Functions'''
    def map(self, area_from=None, exit_from=None):
        is_new_mapping = False

        # # if area_from is not None and exit_from is not None:
        #     # if exit_from.opposite is not None:
        #         # if self.exit_type.id == exit_from.opposite.id:
        #             # area_exit.area_to = area_from  # No, this isn't always true, east, then west, lots of places that doesn't work, like forests, caves, mazes
        #     #else:
        #         '''code a case to handle this exit issue on opposites (west opposite out)
        #         since most of the exit types are likely going to have hardcoded opposite at first
        #         and then especially for exceptions like this it might not be worth the effort
        #         A github issue will be made'''

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

    def pretty_string(self):
        # return f"Area: {str(self.area)},"+ '\nArea Exits '.join(Area Exits: {str(s) for s in self.area_exits)}"
        # return f"Area: {str(self.area)},"+ '\nArea Exit: '+'\nArea Exit n: '.join(str(s) for s in self.area_exits)
        return "AreaExit ... : \n" + \
            "    .exit_type.name : " + str(self.exit_type.name if hasattr(self.exit_type, 'name'      ) else "<None>") + "\n" + \
            "    .area_from.id   : " + str(self.area_from.id   if hasattr(self.area_from, 'id'        ) else "<None>") + "\n" + \
            "    .area_to.id     : " + str(self.area_to.id     if hasattr(self.area_to,   'id'        ) else "<None>") + "\n" + \
            "    .id             : " + str(self.id             if hasattr(self,           'id'        ) else "<None>") + "\n" + \
            "    .exit_type.id   : " + str(self.exit_type.id   if hasattr(self.exit_type, 'id'        ) else "<None>") + "\n" + \
            "    .is_useable     : " + str(self.is_useable     if hasattr(self,           'is_useable') else "<None>") + "\n" + \
            "    .is_hidden      : " + str(self.is_hidden      if hasattr(self,           'is_hidden' ) else "<None>") + "\n"
    def shorter_pretty_string(self):
        return f"{self.exit_type.name} -> "+str(self.area_to.id if hasattr(self.area_to, 'id') else "<None>")

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

    # def get_area_exit_by_from_areaid_and_exit_type_id(from_areaid, exit_type_id):
    #     try:
    #         for areaexit in AreaExit.select().where((AreaExit.area_from == from_areaid) & (AreaExit.exit_type == exit_type_id)):
    #             return areaexit
    #     except AreaExit.DoesNotExist:
    #         return None
    # def get_area_exit_by_from_areaid_and_exit_string(from_areaid, exit_string_partial):
    #     try:
    #         for areaexit in AreaExit.select().where((AreaExit.area_from == from_areaid) & (AreaExit.exit_type == exit_type_id)):
    #             return areaexit
    #     except AreaExit.DoesNotExist:
    #         return None

    def get_area_exits_from_area(area):
        area_exits = []
        try:
            for ae in AreaExit.select().where((AreaExit.area_from == area.id)):
                area_exits.append(ae)
        except AreaExit.DoesNotExist:
            area_exits = []

        return area_exits

    def get_area_exits_from_area_given_areaid(areaid):
        area_exits = []
        try:
            for areaexit in AreaExit.select().where((AreaExit.area_from == areaid)):
                area_exits.append(areaexit)
        except AreaExit.DoesNotExist:
            area_exits = []

        return area_exits































