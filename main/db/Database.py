
'''
Install Peewee to use this
http://peewee.readthedocs.org/en/latest/peewee/installation.html
'''

import peewee
import sys, os, shutil

db = peewee.Proxy()

from db.BaseModel import *
from db.Log import *
from db.Area import *
from db.AreaExit import *
from db.ExitType import *
from db.Mob import *
from db.MobLocation import *
from db.MobMessage import *
from db.Item import *
from db.ItemType import *
from db.ItemTypeModel import *
from db.ItemTypeData import *
from db.AreaStoreItem import *
from db.MudMap import *
from db.MobLoot import *

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

def create_tables():
    try:
        try_create(MobLoot)
        try_create(MobMessage)
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

    except Exception as e:
        # print("Database.py ignoring exception in create_tables(): "+str(e))
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
        try_drop(MobMessage)
        try_drop(Item)
        try_drop(ItemType)
        try_drop(ItemTypeModel)
        try_drop(ItemTypeData)
        try_drop(AreaStoreItem)
    except Exception as e:
        # print("Database.py ignoring exception in drop_tables(): "+str(e))
        pass

def try_create(cls):
    try:
        cls.create_table()
    except Exception as e:
        # print("Database.py ignoring exception in try_create(): "+str(e))
        pass

def try_drop(cls):
    try:
        cls.drop_table()
    except Exception as e:
        # print("Database.py ignoring exception in try_drop(): "+str(e))
        pass

db_name = "maplos.db"
# check if the config.env file exists
if '-nodb' in sys.argv:
    db_name = "no.db"
elif not os.path.isfile('dev-config.env'):    
    # the prescence of this file indicates that we are running in dev mode    
    # copy the maplos-latest.db file overtop of the maplos.db file
    # this will ensure that we are always running with the latest db schema

    if os.path.isfile('maplos-latest.db'):
        # copy the maplos-latest.db file overtop of the maplos.db file
        shutil.copyfile('maplos-latest.db', 'maplos.db')

database = SqliteDatabase(db_name, check_same_thread=False)
db.initialize(database)


#drop_tables()
create_tables()
