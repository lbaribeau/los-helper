from peewee import *
from BaseModel import BaseModel
from misc_functions import *

class Area(BaseModel):
    name = CharField() #Chapel
    description = CharField(null=True) #This will only be used for crawler comparisons
    is_always_dark = BooleanField(default=False)
    is_dark_at_night = BooleanField(default=False)
    is_restorative = BooleanField(default=False)
    #does_damage_on_entry = BooleanField(default=False)
    #teleports_character = Area(null=True)

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
                    #magentaprint("Updating AreaExit with: \n" + area_exit_from.to_string())

        return is_new_mapping

    def search_for_area(self, mapped_exits):
        is_new_mapping = True
        matching_areas = Area.get_areas_by_name_and_description(self.name, self.description)
        for area in matching_areas: #we selected based on name / description so we know they match but just in case or if our descriptions are null
            if (area.has_exits(mapped_exits)):
                self.id = area.id
                self.is_always_dark = area.is_always_dark
                self.is_dark_at_night = area.is_dark_at_night

                #update the database with the longest description possible
                if (len(self.description) > len(str(area.description))):
                    super(Area, self).save()
                else:
                    self.description = area.description

                is_new_mapping = False
                return is_new_mapping #we want to stop the search if we've found a match

        return is_new_mapping

    def has_exits(self, exits): #receiving mapped exits with IDs so we just do a compare on the Area Links
        area_exits = AreaExit.get_area_exits_from_area(self)
        has_exits = (area_exits.count() == len(exits))

        contains_hidden = False

        for area_exit in area_exits:
            if area_exit.is_hidden:
                contains_hidden = True
                break

        if (has_exits or contains_hidden): #if the number of exits we have is the same
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
            areas = Area.select().where((Area.name == area_name))# & (Area.description == area_description))

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

from AreaExit import *