'''In order for this class to work you need to have installed Peewee
See: http://peewee.readthedocs.org/en/latest/peewee/installation.html
'''
from peewee import *

db = Proxy()

from misc_functions import *
from Logging import *
from Area import *
from AreaExit import *
from ExitType import *
from Mob import *
from MobLocation import *
from Item import *
from ItemType import *
from ItemTypeModel import *
from ItemTypeData import *
from AreaStoreItem import *
from MudMap import *

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

from database_setup import *