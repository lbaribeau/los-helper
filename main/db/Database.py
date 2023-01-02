
'''
Install Peewee to use this
http://peewee.readthedocs.org/en/latest/peewee/installation.html
'''

import peewee
import sys

db = peewee.Proxy()

#import db as db_package
from db.BaseModel     import BaseModel
from db.Log           import Log
from db.Area          import Area
from db.AreaExit      import AreaExit
from db.ExitType      import ExitType
from db.Mob           import Mob
from db.MobLocation   import MobLocation
from db.Item          import Item
from db.ItemType      import ItemType
from db.ItemTypeModel import ItemTypeModel
from db.ItemTypeData  import ItemTypeData
from db.AreaStoreItem import AreaStoreItem
from db.MudMap        import MudMap
#from misc_functions import magentaprint # Circular import?

create_view_named_mobs = """
CREATE VIEW [v_named_mobs] AS 
select *
from mob
where name != lower(name);"""
create_view_areas_inc_dirt = """CREATE VIEW [v_areas_inc_dirt] AS 
select a.*, 1 as Derp
from area as a;"""
create_view_exits_for_graph = """CREATE VIEW [v_areaexits_for_graph] AS 
select ae.id, ae.area_from_id, coalesce(ae.area_to_id, 1) as area_to_id, ae.exit_type_id, ae.is_useable, ae.note, ae.is_hidden
from areaexit as ae
where ae.is_useable = 1;"""
create_view_areas_for_graph = """CREATE VIEW [v_areas_for_graph] AS 
select a.* from area as a
where a.id in (
      select distinct(area_from_id)
      from v_areaexits_for_graph);"""

# Add items joined to area store items (we have a view for that)

def create_tables():
    try:
        try_create(db.Log.Log)
        try_create(db.Area.Area)
        try_create(db.AreaExit.AreaExit)
        try_create(db.ExitType.ExitType)
        try_create(db.ExitOpposite.ExitOpposite)
        try_create(db.ExitSynonym.ExitSynonym)
        try_create(db.Mob.Mob)
        try_create(db.MobLocation.MobLocation)
        try_create(db.Item.Item)
        try_create(db.ItemType.ItemType)
        try_create(db.ItemTypeModel.ItemTypeModel)
        try_create(db.ItemTypeData.ItemTypeData)
        try_create(db.AreaStoreItem.AreaStoreItem)
        db.execute_sql(create_named_mobs_view)
        db.execute_sql(create_view_areas_inc_dirt)
        db.execute_sql(create_view_exits_for_graph)
        db.execute_sql(create_view_areas_for_graph)

        #Load Preliminary Data
        Unknown = Area(name="Unknown", description="")
        Unknown.save()

    except Exception as e:
        print("Database.py ignoring exception in create_tables(): "+str(e))
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
    except Exception as e:
        print("Database.py ignoring exception in drop_tables(): "+str(e))
        pass

def try_create(cls):
    try:
        cls.create_table()
    except Exception as e:
        print("Database.py ignoring exception in try_create(): "+str(e))
        pass

def try_drop(cls):
    try:
        cls.drop_table()
    except Exception as e:
        print("Database.py ignoring exception in try_drop(): "+str(e))
        pass

if "-nodb" in sys.argv:
    db.initialize(peewee.SqliteDatabase("no.db", check_same_thread=False))
else:
    db.initialize(peewee.SqliteDatabase("maplos.db", check_same_thread=False))

#database = peewee.SqliteDatabase(database_file, threadlocals=True, check_same_thread=False)
#database2 = peewee.SqliteDatabase(database_file, check_same_thread=False)
#db.initialize(database2)
#db.initialize(peewee.SqliteDatabase(database_file, check_same_thread=False))
#db = database

#drop_tables()
create_tables()
