from peewee import *
import networkx

from db.Database import *
# from misc_functions import *
from misc_functions import do_magentaprint
from comm.ConsoleHandler import newConsoleHandler

def get_shortest_array(list_of_arrays):
    if list_of_arrays == []:
        # magentaprint
        return [] # Let's not crash here with ValueError: min() arg is an empty sequence

    # lengths = []
    # for array in list_of_arrays:
    #     lengths.append(len(array))
    lengths = [len(a) for a in list_of_arrays]

    return list_of_arrays[
        lengths.index(min(lengths, key=int))
    ]

# def get_shortest_array(list_of_arrays):
#     min(lengths, key=int) # problem if length is empty
#     #return list_of_arrays[lengths.index(min(lengths, key=int))]
#     #return min(list_of_arrays, key=len)

class MudMap(object):
    # def magentaprint(self, text):
    #     newConsoleHandler().magenta()
    #     print(text)
    #     newConsoleHandler().white()

    def __init__(self):
        # magentaprint("MudMap: initialized.")
        # los_map = None
        # self.ready = False
        self.re_map()
        # print("MudMap initialized, los_map: " + str(self.los_map))

    def re_map(self):
        self.ready = False
        self.los_map = networkx.DiGraph()
        self.populate_map()
        self.ready = True

    def populate_map(self):
        # do_magentaprint("MudMap populate_map doing areas...") # str(areas)
        for area in Area.raw('select * from v_areas_for_graph'):
            self.los_map.add_node(area.id)

        do_magentaprint("MudMap did the areas now doing area_exits.")
        for area_exit in AreaExit.raw('select * from v_areaexits_for_graph'):
            self.los_map.add_edge(
                area_exit.area_from.id, 
                area_exit.area_to.id, 
                name=area_exit.exit_type.name
            )

        do_magentaprint("MudMap populate_map finished the area_exits).")

            # area_to_id = -1 #this is a marker for a null / unexplored area
            # area_is_useable = True

            # if area_exit.area_to is not None:
            #     area_to_id = area_exit.area_to.id
            #     area_is_useable = area_exit.is_useable
            #     #do_magentaprint("area useable: " + str(area_is_useable) + " " + str(area_exit.is_useable), False)

            # if area_is_useable: #don't add unusable areas to the graph
            #     name = area_exit.exit_type.name
            #     self.los_map.add_edge(area_exit.area_from.id, area_to_id, name=name)

    def to_string(self):
        return str(self.los_map.nodes()) + "\n\n" + str(self.los_map.edges())

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def get_path(self, start_area_id, end_area_id):
        # do_magentaprint("MudMap.get_path() los_map: {0}, start: {1}, end: {2}".format(self.los_map, start_area_id, end_area_id))
        try:
            node_path = networkx.shortest_path(self.los_map, source=start_area_id, target=end_area_id)
        except Exception as e:
            do_magentaprint("MudMap: " + str(e))
            raise e

        edge_path = []
        i = 0
        while i < len(node_path) - 1:
            # do_magentaprint("MudMap looping... " + str(i))
            # cur_edge = self.los_map.get_edge_data(node_path[i], node_path[i+1])
            # edge_path.append(cur_edge['name'])
            edge_path.append(self.los_map.get_edge_data(node_path[i], node_path[i+1])['name'])
            i += 1

        # edge_path = [self.los_map.get_edge_data(N[i-1], N[i])['name'] for i in range(1,len()) 
        #do_magentaprint("MudMap: Node path: " + str(node_path), False)
        do_magentaprint("MudMap.get_path() got path of length {0}.".format(len(edge_path)))
        return edge_path

    def get_nearest_unexplored_path(self, start_area_id):
        return self.get_path(start_area_id, 1)

    def get_paths_to_restorative_area(self, start_area_id):
        paths = []
        areas = Area.get_restorative_areas()
        for area in areas:
            try:
                paths.append(self.get_path(start_area_id, area.id))
            except Exception as e:
                continue
                # print ("couldn't path to area")
                # do_magentaprint("couldn't path to area")

        return paths

    def get_smithy_paths(self, start_area_id):
        paths = []
        areas = Area.get_smithy_areas()
        for area in areas:
            try:
                paths.append(self.get_path(start_area_id, area.id))
            except Exception as e:
                continue
                # print ("couldn't path to area")
                # do_magentaprint("couldn't path to area")

        return paths

    def get_pawn_paths(self, start_area_id):
        paths = []
        areas = Area.get_pawn_shops()
        for area in areas:
            try:
                paths.append(self.get_path(start_area_id, area.id))
            except Exception as e:
                continue
                # print ("couldn't path to area")
                # do_magentaprint("couldn't path to area")
        return paths

    def get_tip_paths(self, start_area_id):
        paths = []
        areas = Area.get_tips()
        for area in areas:
            try:
                paths.append(self.get_path(start_area_id, area.id))
            except Exception as e:
                continue
        return paths

    def get_path_to_nearest_restorative_area(self, start_area_id):
        # We will need evil restorative areas and good restorative areas
        return get_shortest_array(self.get_paths_to_restorative_area(start_area_id))
    def get_path_to_nearest_smithy(self, start_area_id):
        return get_shortest_array(self.get_smithy_paths(start_area_id))
    def get_path_to_nearest_pawn_shop(self, start_area_id):
        return get_shortest_array(self.get_pawn_paths(start_area_id))
    def get_path_to_nearest_tip(self, start_area_id):
        return get_shortest_array(self.get_tip_paths(start_area_id))

    #static functions
    def find(text):
        # text can be an area or a mob name
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

    def next_node(self, aid, exit_name):
        # do_magentaprint(str(self.mud_map.los_map[self.character.AREA_ID]))
        node_dict = self.los_map[aid]
        for n in node_dict.keys():
            # (Pdb) print g[5]
            # {15: {'name': 'east'}, 16: {'name': 'town hall'}, 3: {'name': 'north'}, 7: {'name': 'west'}}
            if node_dict[n]['name'] == exit_name:
                return n
        return -1

    def lookup_armour_type(self, armour_name):
        # Body, arms, etc
        # item = Item(armour_name)
        # item.map()
        return Item.lookup_armour_type(armour_name)

