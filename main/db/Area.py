import sys
from peewee import *
from misc_functions import *
from db.NamedModel import NamedModel

class Area(NamedModel):
    description = CharField(null=True) #This will only be used for crawler comparisons
    is_always_dark = BooleanField(default=False)
    is_dark_at_night = BooleanField(default=False)
    is_restorative = BooleanField(default=False)
    #does_damage_on_entry = BooleanField(default=False)
    #teleports_character = Area(null=True)

    class metadata:
        def __init__(self):
            self.is_dirty = False

        def is_dirty(self):
            is_dirty

    '''Private Area Functions'''
    def map(self, exits, cur_area_from=None, cur_exit_from=None):
        is_new_mapping = True
        is_new_exit_mapping = False

        mapped_exits = []
        for exit in exits:
            exit.map() # this will update our exit objects with their corresponding ids
            mapped_exits.append(exit)

        is_new_mapping = self.search_for_area(mapped_exits)

        #if (cur_area_from is None):
            
        #elif (cur_area_from.name != self.name): #if the names are the same then this is a new area since we have moved
        #    is_new_mapping = self.search_for_area(mapped_exits)

        if is_new_mapping: #this means the search has found the matching area and our Area.ID is set
            super().save()  # Db can be locked if this happens immediately...

            #now we map our area exits
            for exit in mapped_exits:
                #magentaprint("exit " + str(exit.to_string()), False)
                area_exit = AreaExit(area_from=self.id, area_to=None, exit_type=exit)

                '''if (exit_from.opposite is None):
                    if (exit.id == exit_from.opposite.id):
                        area_exit.map(area_from, exit_from)
                    else:'''

                area_exit.map()
                is_new_exit_mapping = True

        #last but not least we want to try to update our area_from with it's area_to value :)
        if cur_area_from is not None and cur_exit_from is not None:
            area_exit_from = AreaExit.get_area_exit_by_area_from_and_exit_type(cur_area_from, cur_exit_from)
            if (area_exit_from is not None):
                if (area_exit_from.area_to is None): #don't overwrite values that have been
                    area_exit_from.area_to = self
                    area_exit_from.save()
                    #magentaprint("Updating AreaExit with: \n" + area_exit_from.to_string())

        return is_new_mapping, is_new_exit_mapping

    def search_for_area(self, mapped_exits):
        is_new_mapping = True

        matching_areas = Area.get_areas_by_name_and_exits(self.name, mapped_exits, self.description)

        #print ("matching areas: " + str(matching_areas) + " is new mapping: " + str(is_new_mapping))

        if len(matching_areas) > 0:
            self.metadata.is_dirty = True
            is_new_mapping = False
            
            for area in matching_areas:
                self.id = area.id
                self.is_always_dark = area.is_always_dark
                self.is_dark_at_night = area.is_dark_at_night
                self.is_restorative = area.is_restorative
                break

        #print ("matching areas: " + str(matching_areas) + " is new mapping: " + str(is_new_mapping))

        if not self.metadata.is_dirty:
            #update the database with the longest description possible
            if (len(self.description) > len(str(area.description))):
                super(Area, self).save()
            else:
                self.description = area.description

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
        return str(self.id) + ", " + self.name

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    '''Static Area Functions'''
    def get_areas_by_name(area_name):
        areas = []

        try:
            areas = Area.select().where((Area.name == area_name))

        except Area.DoesNotExist:
            areas = []

        return areas

    def get_areas_by_name_and_description(area_name, area_description):
        areas = []

        try:
            areas = Area.select().where((Area.name == area_name) & (Area.description == area_description))

        except Area.DoesNotExist:
            areas = []

        return areas

    def get_areas_by_name_and_exits(area_name, exit_type_list, area_description=""):
        areas = []
        exit_id_list = ""
        exit_count = len(exit_type_list)
        description_clause = ""

        if area_description != "":
            description_clause = " and a.description = '%s'" % area_description.replace("'", "''")

        if (exit_count > 0):
            exit_id_list += str(exit_type_list[0].id)
            for i in range(1, exit_count):
                exit_id_list += ", " + str(exit_type_list[i].id)

            try:
                query ="""
select a.*
from area a
join areaexit as ae
on a.id = ae.[area_from_id]
where a.id in (
select ae.area_from_id
from areaexit as ae
join area as a
on a.id = ae.area_from_id
where a.name = "%s"%s and ae.is_hidden = 0
group by ae.area_from_id
having count(*) = %s
) and ae.[exit_type_id] in (%s)
group by a.id
having count(*) = %s
"""

                formatted_query = query % (area_name, description_clause, str(exit_count), exit_id_list, str(exit_count))

                # print (formatted_query)

                for derp in Area.raw(formatted_query):
                    areas.append(derp)

            except Area.DoesNotExist:
                areas = []
        else:
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

    def get_restorative_areas():
        areas = []

        try:
            areas = Area.select().where((Area.is_restorative == 1))

        except Area.DoesNotExist:
            areas = []

        return areas

from db.AreaExit import *
from db.ExitType import *