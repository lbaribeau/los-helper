'''In order for this class to work you need to have installed Peewee
See: http://peewee.readthedocs.org/en/latest/peewee/installation.html
'''
import peewee

db = peewee.Proxy()

from db.BaseModel import *
from db.Log import *
from db.Area import *
from db.AreaExit import *
from db.ExitType import *
from db.Mob import *
from db.MobLocation import *
from db.Item import *
from db.ItemType import *
from db.ItemTypeModel import *
from db.ItemTypeData import *
from db.AreaStoreItem import *
from db.MudMap import *

def create_tables():
    try:
        try_create(Log)
        try_create(Area)
        try_create(AreaExit)
        try_create(ExitType)
        try_create(ExitOpposite)
        try_create(ExitSynonym)
        try_create(Mob)
        try_create(MobLocation)
        try_create(Item)
        try_create(ItemType)
        try_create(ItemTypeModel)
        try_create(ItemTypeData)
        try_create(AreaStoreItem)

        #Create Views
        db.execute_sql("""CREATE VIEW [v_named_mobs] AS 
select *
from mob
where name != lower(name);""")

        db.execute_sql("""CREATE VIEW [v_areas_inc_dirt] AS 
select a.*, 1 as Derp
from area as a;""")

        db.execute_sql("""CREATE VIEW [v_areaexits_for_graph] AS 
select ae.id, ae.area_from_id, coalesce(ae.area_to_id, 1) as area_to_id, ae.exit_type_id, ae.is_useable, ae.note, ae.is_hidden
from areaexit as ae
where ae.is_useable = 1;""")

        db.execute_sql("""CREATE VIEW [v_areas_for_graph] AS 
select a.* from area as a
where a.id in (
      select distinct(area_from_id)
      from v_areaexits_for_graph);""")

        #Load Preliminary Data
        Unknown = Area(name="Unknown", description="")
        Unknown.save()

    except:
        pass

def drop_tables():
    try:
        try_drop(Log)
        try_drop(Area)
        try_drop(AreaExit)
        try_drop(ExitType)
        try_drop(ExitOpposite)
        try_drop(ExitSynonym)
        try_drop(Mob)
        try_drop(MobLocation)
        try_drop(Item)
        try_drop(ItemType)
        try_drop(ItemTypeModel)
        try_drop(ItemTypeData)
        try_drop(AreaStoreItem)
    except:
        pass

def try_create(cls):
    try:
        cls.create_table()
    except:
        pass

def try_drop(cls):
    try:
        cls.drop_table()
    except:
        pass

from sys import argv

if "-nodb" in argv:
    database_file = "no.db"
else:
    database_file = "maplos.db"

database = peewee.SqliteDatabase(database_file, threadlocals=True, check_same_thread=False)
db.initialize(database)

#drop_tables()
create_tables()