'''In order for this class to work you need to have installed Peewee
See: http://peewee.readthedocs.org/en/latest/peewee/installation.html
'''
from peewee import *

global db

class LOSDatabase():
    def __init__(self, dbfile):
        self.db = SqliteDatabase(dbfile)
        self.db.connect()

    def get_db(self):
        return self.db

db = LOSDatabase("los-test.db").get_db()

class BaseModel(Model):
    class Meta:
        database = db

class Area(BaseModel):
    name = CharField() #Chapel
    description = CharField() #This will only be used for crawler comparisons

    def toString(self):
        return str(self.id) + ", " + self.name + ", " + str(self.description)

class DirectionType(BaseModel):
    name = CharField() #ex. n, out, door
    primer = CharField(null=True) #ex. open %s, unlock %s key

    def toString(self):
        return str(self.id) + ", " + self.name + ", " + str(self.primer)

class AreaLink(BaseModel):
    areaFrom = ForeignKeyField(Area, related_name='areaFrom') #id is a default attribute
    areaTo = ForeignKeyField(Area, related_name='areaTo') #id is a default attribute
    directionType = ForeignKeyField(DirectionType)

    def toString(self):
        return str(self.id) + ", " + str(self.areaFrom.name) + ", " + str(self.areaTo.name) + ", " + str(self.directionType.name)

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