from Database import *
from misc_functions import *

class MudArea():
    area = None
    area_exits = []

    def __init__(self, area, area_exits=None):
        if self.area is not None or area is not None:
            if self.area is None:
                self.area = area

            if area_exits is None and self.area:
                self.area_exits = AreaExit.get_area_exits_from_area(area)
            else:
                self.area_exits = area_exits
        else:
            print ("Area is null for some awful reason.")

    @staticmethod
    def map(area_title, area_description, exit_list, area_from, direction_from, cur_mud_area):
        direction_list = []
        area = Area(name=str(area_title), description=str(area_description).replace("\n\r", ' '))
        mud_area = None
        area_exits = None

        for exit in exit_list:
            exit_type = ExitType(name=str(exit))
            exit_type.map()
            direction_list.append(exit_type)

        discerned_area = MudArea.discern_location(area, direction_list, area_from, direction_from, cur_mud_area)

        if discerned_area is not None:
            area = discerned_area.area
        else:
            if area_from is not None and direction_from is not None: #if we have an area we're coming from
                area_from = Area.get_area_by_id(area_from)
                direction_from = ExitType.get_exit_type_by_name_or_shorthand(direction_from)

                # magentaprint("MudArea: " + str(area_from) + " " + str(direction_from))
                
                area.map(direction_list, area_from, direction_from)
            else:
                area.map(direction_list)

            area_exits = AreaExit.get_area_exits_from_area(area)

        return MudArea(area, area_exits)

    @staticmethod
    def discern_location(area, direction_list, area_from_id, direction_from, cur_mud_area):
        discerned_area = None

        if cur_mud_area is not None:
            exit_type = ExitType.get_exit_type_by_name_or_shorthand(direction_from)

            if exit_type is None:
                exit_type = ExitType(name=direction_from)
            
            discerned_area = cur_mud_area.get_area_to_from_exit(exit_type)

            #if isNewExit: - this is logic we can implement once we have exit_type mapping completely bullet proof

            # magentaprint("MudArea discerning: " + str(cur_mud_area) + " against " + str(area))

        return discerned_area

    @staticmethod
    def set_area_exit_as_unusable(regex, area_from, exit_type):
        if area_from is not None and exit_type is not None:
            area_from = Area.get_area_by_id(area_from)
            exit_type = ExitType.get_exit_type_by_name_or_shorthand(exit_type)
            area_exit = AreaExit.get_area_exit_by_area_from_and_exit_type(area_from, exit_type)

            if area_exit is not None:
                area_exit.is_useable = False
                area_exit.note = str(regex)
                area_exit.save()

    def get_area_to_from_exit(self, exit_type):
        area = None

        for areaexit in self.area_exits:
            if areaexit.exit_type.name == exit_type.name:
                if areaexit.area_to is not None:
                    area = MudArea(areaexit.area_to)
                    break

        return area

    def compare_to_area_and_exit_list(self, area, exit_list):
        matchFound = True

        if self.area.name == area.name and len(exit_list) <= len(self.area_exits):
            for areaexit in self.area_exits:
                if not areaexit.is_hidden:
                    matchedExit = False
                    for exit in exit_list:
                        if exit.name == areaexit.exit_type.name:
                            matchedExit = True
                            break
                    if not matchedExit:
                        matchFound = False
                        break
        else:
            matchFound = False

        return matchFound

    def to_string(self):
        return str(self.area) + str(self.area_exits)[1:-1]

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()