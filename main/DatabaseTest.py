import sys, os, inspect

def import_subdir(subdir):
    # use this if you want to include modules from a subforder
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],subdir)))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

import_subdir('../')

from Database import *
from MudMap import *
import networkx as nx
import matplotlib.pyplot as plt

home = Area.get_area_by_id(45) #Chapel
n = ExitType.get_exit_type_by_name("north")
s = ExitType.get_exit_type_by_name("south")
e = ExitType.get_exit_type_by_name("east")
w = ExitType.get_exit_type_by_name("west")
ne = ExitType.get_exit_type_by_name("northeast")
nw = ExitType.get_exit_type_by_name("northwest") 
se = ExitType.get_exit_type_by_name("southeast") 
sw = ExitType.get_exit_type_by_name("southwest")
out = ExitType.get_exit_type_by_name("out")
ame = ExitType.get_exit_type_by_name("amethyst")
chapel = ExitType.get_exit_type_by_name("chapel")

def main():
    #create_database()
    #create_dataset()

    database = SqliteDatabase('maplos.db', check_same_thread=False)
    db.initialize(database)
    db.connect()
    create_tables()

    #map_pathing_test()
    #area_ambiguity_test()
    mud_area_cartography_test()
    
    db.close()

def map_pathing_test():
    #MudMap.find("bull")
    #MudMap.find("ranch")
    mud_map = MudMap()

    path = []

    path.extend(mud_map.get_path(45, 1426).direction_list)
    path.extend(mud_map.get_path(1426, 1429).direction_list)
    path.extend(mud_map.get_path(1429, 1427).direction_list)
    path.extend(mud_map.get_path(1427, 1430).direction_list)
    path.extend(mud_map.get_path(1430, 1428).direction_list)
    path.extend(mud_map.get_path(1428, 1431).direction_list)
    path.extend(mud_map.get_path(1431, 45).direction_list)

    print (str(path))

def mud_area_cartography_test():
    mud_area_cartography_unit_test(home, out, "Holly Lane", [n, s, chapel])
    mud_area_cartography_unit_test(home, out, "Holly Lane", [n, s, w])

    cartway = Area.get_area_by_id(166)
    mud_area_cartography_unit_test(cartway, e, "The Cartway", [w, e])

    cartway = Area.get_area_by_id(167)
    mud_area_cartography_unit_test(cartway, e, "The Cartway", [w, e])


def mud_area_cartography_unit_test(lastArea, lastDirection, curAreaName, direction_list):
    magentaprint("Travelled '%s' from '%s'" % (lastDirection.name, lastArea.name), False)

    lastMudArea = MudArea(lastArea)
    curMudArea = lastMudArea.get_area_to_from_exit(lastDirection)
    area = Area(name=str(curAreaName), description=str(""))

    magentaprint(curMudArea.area, False)

    cur_exit_list = []

    for exit in curMudArea.area_exits:
        cur_exit_list.append(exit.exit_type.name + ", hidden: " + str(exit.is_hidden))

    magentaprint("We see: %s\nthe area we should be at has: %s" % (direction_list, cur_exit_list), False)

    magentaprint(str(curMudArea.compare_to_area_and_exit_list(area, direction_list)), False)
    print("---------\n\n")

def area_ambiguity_test():
    ambiguity_unit_test("Forest Path", [e, w])
    ambiguity_unit_test("The Cartway", [e, w])
    ambiguity_unit_test("Limbo", [ame])
    ambiguity_unit_test("Holly Lane", [n, s, chapel])


def ambiguity_unit_test(area_name, exit_type_list):
    output_template = "Get all areas with name '%s' with exits '%s'"

    magentaprint(output_template % (area_name, str(exit_type_list)), False)

    areas = Area.get_areas_by_name_and_exits(area_name, exit_type_list)

    for area in areas:
        magentaprint(area, False)
        areaexits = AreaExit.get_area_exits_from_area(area)

        for ae in areaexits:
            magentaprint(ae, False)

        print("\n")

    print("---------\n\n")


main()
