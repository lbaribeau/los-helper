import sys
from Database import *

def main():
    #create_database()
    #create_dataset()

    



    database = SqliteDatabase('map.db', check_same_thread=False)
    db.initialize(database)

    dirNorth = DirectionType(name='north')
    dirSouth = DirectionType(name='south')
    dirEast = DirectionType(name='east')

    areaHollyLane = Area(name='Holly Lane')
    areaHollyLane.map([dirNorth, dirSouth, dirEast])

    links = AreaLink.get_area_links_from_area(areaHollyLane)

    for link in links:
        print ("    " + link.to_string())

    #print ("   Area From: " + Area1.to_string() + "\n   Area To: " + Area2.to_string())

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