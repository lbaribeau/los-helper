
import peewee
from db.Database import db
#from db.Area import Area
#db.initialize(peewee.SqliteDatabase('../maplos.db', check_same_thread=False))
db.connect()
#db.execute_sql("SELECT * FROM area;")
# Reminder: back up db file
db.execute_sql("ALTER TABLE area ADD is_pawn_shop BOOL")
db.execute_sql("ALTER TABLE area ADD is_tip BOOL")
#db.execute_sql("ALTER TABLE area MODIFY COLUMN is_smithy BOOL") # not ALTER COLUMN in MySQL
#db.execute_sql("ALTER TABLE area MODIFY is_smithy BOOL") # is_smithy can stay an INT
#https://www.w3schools.com/sql/sql_alter.asp

#b=BoolField()
# Maybe just edit the db instead of finding a peewee way to do it
# Because peewee is runtime

#db.create_tables([Area], safe=True)


