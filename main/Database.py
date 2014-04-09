'''In order for this class to work you need to have installed Peewee
See: http://peewee.readthedocs.org/en/latest/peewee/installation.html
'''
from peewee import *
import misc_functions

db = SqliteDatabase("los" + str(misc_functions.VERSION) + ".db")
db.connect()

class BaseModel(Model):
    class Meta:
        database = db

class Area(BaseModel):
    name = CharField() #Chapel
    description = CharField(null=True) #This will only be used for crawler comparisons

    def toString(self):
        return str(self.id) + ", " + self.name + ", " + str(self.description)

class DirectionType(BaseModel):
    name = CharField() #ex. north, out, door
    shorthand = CharField(null=True) #user input alternative North == n
    primer = CharField(null=True) #ex. open %s, unlock %s key
    opposite = ForeignKeyField('self', null=True)

    def toString(self):
        return str(self.id) + ", " + self.name + ", " + str(self.primer) + ", " + str(self.opposite)

class AreaLink(BaseModel):
    areaFrom = ForeignKeyField(Area, related_name='areaFrom') #id is a default attribute
    areaTo = ForeignKeyField(Area, related_name='areaTo', null=True) #id is a default attribute
    directionType = ForeignKeyField(DirectionType)

    def getAreaToName(self):
        if (self.areaTo is not None):
            return self.areaTo.name
        else:
            return None

    def toString(self):
        return str(self.id) + ", " + str(self.areaFrom.name) + ", " + str(self.getAreaToName()) + ", " + str(self.directionType.name)

def mapArea(area, directions, areaFrom=None, directionFrom=None):
    #first things first - we want to get the ids of these directions
    #this way we can compare the AreaLinks of the given Area
    #also if we discover a brand new direction we've guaranteed the area is new
    isNew = False
    dTypes, includesNewDirection = mapDirections(directions)

    output = None
    obj = getAreaByNameAndDirections(area, dTypes)

    if (obj is None or includesNewDirection): #we're definitely creating a new area
        area.save()
        output = area
        isNew = True

        #only add new links to new areas
        aLinks, includesNewLinks = mapLinks(output, dTypes)
    else: #this area seems to already exist
        output = obj

    #if (areaFrom is not None and directionFrom is not None):
    #update the AreaLink with the correct areaTo id
    #mapAreaLink(areaFrom, directionFrom, output) #outputIsOurArea to :)

    return output

def mapDirections(directions):
    includesNewDirection = False
    dTypes = []

    for directionType in directions:
        dType, isNew = mapDirectionType(directionType)
        dTypes.append(dType)

        if (isNew):
            includesNewDirection = True

    return (dTypes, includesNewDirection)

def mapDirectionType(directionType):
    isNew = False
    obj = getDirectionTypeByName(directionType.name)

    if (obj is None):
        directionType.save()
    else:
        directionType = obj

    return (directionType, isNew)

def mapLinks(areaFrom, directions):
    includesNewLinks = False
    aLinks = []

    for directionType in directions:
        aLink, isNew = mapAreaLink(areaFrom, directionType)
        aLinks.append(aLink)

        if (isNew):
            includesNewLinks = True

    return (aLinks, includesNewLinks)

def mapAreaLink(areaFrom, direction, areaTo=None):
    isNew = False
    temp = genAreaLink(areaFrom, direction, areaTo)

    obj = getAreaLink(temp, direction)

    if (obj is None):
        temp.save()
        isNew = True
    else:
        temp = obj

        if (areaTo is not None and temp.areaTo is None):
            temp.areaTo = areaTo
            temp.save() #update the area :)

    return (temp, isNew)

def genAreaLink(areaFrom, direction, areaTo=None):
    return AreaLink(areaFrom=areaFrom, areaTo=areaTo, directionType=direction)

def getAreaByNameAndDirections(area, dTypes):
    try:
        temp = Area.select().where(Area.name == area.name)
        tempDirectionsMatch = False #I'm an optimist
        output = None

        #if we see more than one area returned from this search we need to loop through
        for curArea in temp:
            tempBool = areaHasDirections(curArea, dTypes)

            print(curArea.toString() + " == " + area.toString() + " == " + str(tempBool))

            tempDirectionsMatch = areaHasDirections(curArea, dTypes)
            if (tempDirectionsMatch):
                return curArea #this is kind of evil since I'm replacing a big list of Area's with a single area but SHUTUP

    except Area.DoesNotExist:
        output = None

    return output

def areaHasDirections(area, directions):
    tempDirections = getAreaDirections(area)
    #check to see if the number of directions in both lists are the same
    hasDirections = (len(tempDirections) == len(directions))

    #print("hasDirections: " + str(hasDirections) + " area: " + str(area.toString()))

    if (hasDirections):
        dNameAInListB = False
        for dTypeA in directions:
            dNameAInListB = False
            for dTypeB in tempDirections:
                if (dTypeA.name == dTypeB.name):
                    dNameAInListB = True
            if not dNameAInListB:
                return False
        hasDirections = dNameAInListB

    return hasDirections

def getAreaDirections(area):
    areaDirections = []

    aLinks = getAreaLinksFromArea(area)
    areaDirections = getDirectionsFromAreaLinks(aLinks)

    return areaDirections

def getAreaLinksFromArea(areaFrom):
    try:
        temp = AreaLink.select().where((AreaLink.areaFrom == areaFrom))
    except AreaLink.DoesNotExist:
        temp = None

    return temp

def getDirectionsFromAreaLinks(areaLinks):
    directions = []

    try:
        for aLink in areaLinks:
            directions.append(getDirectionByID(aLink.directionType))
    except DirectionType.DoesNotExist:
        #This shouldn't happen but stranger things have...
        directions = []

    return directions

def getDirectionTypeByName(directionTypeName):
    try:
        temp = DirectionType.select().where(DirectionType.name == directionTypeName).get()
    except DirectionType.DoesNotExist:
        temp = None

    return temp

def getDirectionByID(directionID):
    try:
        temp = DirectionType.select().where(DirectionType.id == directionID).get()
    except DirectionType.DoesNotExist:
        temp = None
        print("Database select error in getDirectionsFromAreaLinks - direction data missing")
        raise DirectionType.DoesNotExist

    return temp

def getAreaLink(areaFrom, direction):
    try:
        temp = AreaLink.select().where((AreaLink.areaFrom == areaFrom) & (AreaLink.directionType == direction)).get()
    except AreaLink.DoesNotExist:
        temp = None

    return temp

def create_tables():
    try:
        Area.create_table()
        AreaLink.create_table()
        DirectionType.create_table()
    except:
        pass

def drop_tables():
    try:
        Area.drop_table()
        AreaLink.drop_table()
        DirectionType.drop_table()
    except:
        pass