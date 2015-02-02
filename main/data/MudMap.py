from peewee import *
import networkx as nx
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


class MudMap():
    los_map = None

    def __init__(self):
        self.re_map()

    def re_map(self):
        self.los_map = nx.DiGraph()
        self.populate_map()

    def populate_map(self):
        areas = Area.raw('select * from v_areas_for_graph')
        area_exits = AreaExit.raw('select * from v_areaexits_for_graph')

        for area in areas:
            self.los_map.add_node(area.id)

        for area_exit in area_exits:
            name = area_exit.exit_type.name
            self.los_map.add_edge(area_exit.area_from.id, area_exit.area_to.id, name=name)
            '''area_to_id = -1 #this is a marker for a null / unexplored area
            area_is_useable = True
            if (area_exit.area_to is not None):
                area_to_id = area_exit.area_to.id
                area_is_useable = area_exit.is_useable

                #magentaprint("area useable: " + str(area_is_useable) + " " + str(area_exit.is_useable), False)

            if area_is_useable: #don't add unusable areas to the graph
                name = area_exit.exit_type.name
                self.los_map.add_edge(area_exit.area_from.id, area_to_id, name=name)'''

    def to_string(self):
        return str(self.los_map.nodes()) + "\n\n" + str(self.los_map.edges())

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def get_path(self, start_area_id, end_area_id):
        node_path = nx.shortest_path(self.los_map,source=start_area_id,target=end_area_id)
        edge_path = []

        i = 0
        while i < (len(node_path) - 1):
            cur_edge = self.los_map.get_edge_data(node_path[i], node_path[i+1])

            edge_path.append(cur_edge['name'])
            i += 1

        #magentaprint("Got path: " + str(edge_path), False)

        return edge_path

    def get_nearest_unexplored_path(self, start_area_id):
        return self.get_path(start_area_id, -1)


    #static functions
    def find(text):
        areas = Area.get_areas_by_partial_name(text)
        mob_locations = MobLocation.get_locations_by_partial_mob_name(text)

        return [areas, mob_locations]

    def get_mob_locations_by_name(name):
        locations = []
        mob_locations = MobLocation.get_locations_by_exact_mob_name(name)

        for mob_location in mob_locations:
            locations.append(mob_location.area.id)

        return locations

    def get_mob_locations_by_id(mob_id):
        locations = []
        mob_locations = MobLocation.get_locations_by_mob_id(mob_id)

        for mob_location in mob_locations:
            locations.append(mob_location.area.id)

        return locations
