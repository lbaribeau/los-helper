import sys
from Database import *
from MudMap import *
import networkx as nx
import matplotlib.pyplot as plt

def main():
    #create_database()
    #create_dataset()

    database = SqliteDatabase('maplos.db', check_same_thread=False)
    db.initialize(database)
    db.connect()
    create_tables()

    #MudMap.find("bull")
    #MudMap.find("ranch")

    mud_map = MudMap()

    path = []

    path.extend(mud_map.get_path(45, 1426))
    path.extend(mud_map.get_path(1426, 1429))
    path.extend(mud_map.get_path(1429, 1427))
    path.extend(mud_map.get_path(1427, 1430))
    path.extend(mud_map.get_path(1430, 1428))
    path.extend(mud_map.get_path(1428, 1431))
    path.extend(mud_map.get_path(1431, 45))

    print (str(path))

    db.close()

main()