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

    MudMap.find("bull")
    MudMap.find("ranch")

    #mud_map = MudMap()

    #mud_map.get_path(45, 68)
    #mud_map.get_path(68, 71)
    #mud_map.get_path(71, 72)
    #mud_map.get_path(72, 35)
    #mud_map.get_path(35, 45)

    db.close()

main()