from peewee import *
from BaseModel import *
from misc_functions import *
import time
from datetime import datetime

class Log(BaseModel):
    timestamp = DateTimeField(default=datetime.now)
    data = TextField()

    def to_string(self):
        return str(self.timestamp) + ", " + str(self.data)