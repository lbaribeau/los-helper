from Database import *

database_file = "maplos.db"
database = SqliteDatabase(database_file, threadlocals=True, check_same_thread=False)
db.initialize(database)

#drop_tables()
create_tables()