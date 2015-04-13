from peewee import *
import networkx as nx

from Database import *
from misc_functions import *
# from misc_functions import magentaprint

# class MudMap(object):
class MudMap():
    los_map = None
    ready = False

    def __init__(self):
        # magentaprint("MudMap: initialized.")
        self.re_map()
        print("MudMap initialized, los_map: " + str(self.los_map))

    def re_map(self):
        self.ready = False
        self.los_map = nx.DiGraph()
        self.populate_map()
        self.ready = True

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
        magentaprint("MudMap.get_path self.los_map: " + str(self.los_map))
        node_path = nx.shortest_path(self.los_map, source=start_area_id, target=end_area_id)
        edge_path = []

        i = 0
        while i < (len(node_path) - 1):
            cur_edge = self.los_map.get_edge_data(node_path[i], node_path[i+1])

            edge_path.append(cur_edge['name'])
            i += 1

        magentaprint("MudMap: Node path: " + str(node_path), False)
        magentaprint("MudMap: Edge path: " + str(edge_path), False)

        return edge_path

    def get_nearest_unexplored_path(self, start_area_id):
        return self.get_path(start_area_id, 1)

    def get_paths_to_nearest_restorative_area(self, start_area_id):
        paths = []

        areas = Area.get_restorative_areas()

        for area in areas:
            try:
                paths.append(self.get_path(start_area_id, area.id))
            except Exception as e:
                continue
                # print ("couldn't path to area")
                # magentaprint("couldn't path to area")

        return paths


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
