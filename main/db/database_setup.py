
from sys import argv

# from Database import *

if "-nodb" in argv:
	database_file = "no.db"
else:
	database_file = "maplos.db"
	
database = SqliteDatabase(database_file, check_same_thread=False)
db.initialize(database)

# #drop_tables()
# create_tables()