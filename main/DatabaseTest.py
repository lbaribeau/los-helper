import sys
from Database import *

global db
db = LOSDatabase("los-test.db").get_db()


def main():
    #drop_tables()
    #create_tables()

    dirOut = DirectionType(name='out')
    dirChapel = DirectionType(name='chapel')
    dirNorth = DirectionType(name='n')
    dirSouth = DirectionType(name='s')

    dirOut.save()
    dirChapel.save()
    dirNorth.save()
    dirSouth.save()

    areaChapel = Area(name='Chapel', description='Pithy Chapel of sorts')
    areaHollyLane = Area(name='Holly Lane', description='Here be Acolytes')

    areaChapel.save()
    areaHollyLane.save()

    areaHollyLane2 = Area(name='Holly Lane', description='Here be MORE Acolytes')
    areaHollyLane2.save()

    alChapelToHolly = AreaLink(areaFrom=areaChapel, areaTo=areaHollyLane, directionType=dirOut)
    alHollyToChapel = AreaLink(areaFrom=areaHollyLane, areaTo=areaChapel, directionType=dirChapel)
    alHollyToHolly = AreaLink(areaFrom=areaHollyLane, areaTo=areaHollyLane2, directionType=dirNorth)
    alHollyToHolly2 = AreaLink(areaFrom=areaHollyLane2, areaTo=areaHollyLane, directionType=dirSouth)

    alChapelToHolly.save()
    alHollyToChapel.save()
    alHollyToHolly.save()
    alHollyToHolly2.save()

    print ("Outputting Direction Types in the Database")

    for directionType in DirectionType.select():
        print ("    " + directionType.toString())

    print ("\nOutputting Areas in the Database")

    for area in Area.select():
        print ("    " + area.toString())

    print ("\nOutputting Area Links in the Database")

    for aLink in AreaLink.select():
        print ("    " + aLink.toString())

    print ("\n\nSelecting the areas from alHollyToChapel")

    Area1 = Area.select().where(Area.id == alHollyToChapel.areaFrom).get()
    Area2 = Area.select().where(Area.id == alHollyToChapel.areaTo).get()

    print ("   Area From: " + Area1.toString() + "\n   Area To: " + Area2.toString())

    print ("\n\nListing directions")

main()