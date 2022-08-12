
import peewee
import datetime

from db.BaseModel import BaseModel
import misc_functions

class Log(BaseModel):
    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    data      = peewee.TextField()

    def to_string(self):
        return str(self.timestamp) + ", " + str(self.data)

    def magentaprint_and_log(self, text):
        misc_functions.magentaprint(text)
        self.data = text
        self.save()
