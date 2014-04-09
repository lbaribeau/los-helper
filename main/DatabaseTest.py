import sys
from Database import *

def main():
    #create_database()
    create_dataset()

    print ("Outputting Direction Types in the Database")

    for directionType in DirectionType.select():
        print ("    " + directionType.toString())

    print ("\nOutputting Areas in the Database")

    for area in Area.select():
        print ("    " + area.toString())

    print ("\nOutputting Area Links in the Database")

    for aLink in AreaLink.select():
        print ("    " + aLink.toString())

    #print ("   Area From: " + Area1.toString() + "\n   Area To: " + Area2.toString())

def create_database():
    drop_tables()
    create_tables()
    return

def create_dataset():
    dirOut = DirectionType(name='out')
    dirChapel = DirectionType(name='chapel')
    dirNorth = DirectionType(name='n')
    dirSouth = DirectionType(name='s')
    dirTaco = DirectionType(name='taco', primer='salivate')
    dirSouth2 = DirectionType(name='south')
    dirNorth2 = DirectionType(name='ne')

    areaChapel = Area(name='Chapel', description='Pithy Chapel of sorts')
    areaHollyLane = Area(name='Holly Lane', description='Here be Acolytes')

    mapArea(areaChapel, [dirOut])
    mapArea(areaHollyLane, [dirNorth, dirChapel, dirSouth])

    areaHollyLane2 = Area(name='Holly Lane', description='Here be MORE Acolytes')
    mapArea(areaHollyLane2, [dirNorth])

    areaSpain = Area(name='Spain', description='Rawr sauce')

    directions = [dirTaco, dirSouth, dirNorth2]

    savedArea = mapArea(areaSpain, directions)
main()