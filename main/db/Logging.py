from peewee import *
from datetime import datetime
import time

from db.BaseModel import *
from misc_functions import *

class Log(BaseModel):
    timestamp = DateTimeField(default=datetime.now)
    data = TextField()

    def to_string(self):
        return str(self.timestamp) + ", " + str(self.data)