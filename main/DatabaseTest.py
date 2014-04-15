import sys
from Database import *
from MudMap import *

def main():
    #create_database()
    #create_dataset()

    database = SqliteDatabase('map3.db', check_same_thread=False)
    db.initialize(database)
    db.connect()
    #create_tables()

    mud_map = MudMap()

    #print(mud_map.to_string()) #print everything
    print(str(mud_map.get_path(2,24))) #chapel to tip path

    print(str(mud_map.get_nearest_unexplored_path(2))) #nearest unexplored path from chapel

    db.close()


def create_database():
    drop_tables()
    create_tables()
    return

def create_dataset():
    dirOut = DirectionType(name='out')
    dirChapel = DirectionType(name='chapel')
    dirNorth = DirectionType(name='north')
    dirSouth = DirectionType(name='south')
    dirTaco = DirectionType(name='door')
    dirSouth2 = DirectionType(name='south')
    dirNorth2 = DirectionType(name='northeast')

    areaChapel = Area(name='Chapel', description='Pithy Chapel of sorts')
    areaHollyLane = Area(name='Holly Lane', description='Here be Acolytes')

    areaChapel.map([dirOut])
    areaHollyLane.map([dirNorth, dirChapel, dirSouth])

    areaHollyLane2 = Area(name='Holly Lane', description='Here be MORE Acolytes')
    areaHollyLane2.map([dirNorth])

    areaSpain = Area(name='Spain', description='Rawr sauce')
    directions = [dirTaco, dirSouth, dirNorth2]

    areaSpain.map(directions)


main()