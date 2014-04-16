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

    mud_map = MudMap()

    plt.axis('off')
    nx.draw_networkx(mud_map.los_map,pos=None,with_label=True)
    plt.savefig("maplos3.png")

    db.close()

main()