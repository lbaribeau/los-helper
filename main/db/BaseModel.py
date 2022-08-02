
#from peewee import *
import peewee
import sys

#from db.Database import *
#import db.Database
from db import Database
#from db.Database import *
#from misc_functions import *
import comm.ConsoleHandler
from datetime import datetime

class BaseModel(peewee.Model):
    class Meta:
        database = Database.db

    def to_string(self):
        return str(self.id)
    __str__   = to_string
    __repr__  = to_string # Why might this be wrong?
    # def __str__(self):
    #     return self.to_string()
    # def __repr__(self):
    #     return self.to_string()
    def __eq__(self, other): 
        # Say if type is equal
        if type(other) is type(self):
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        if '-fake' in sys.argv:
            print("BaseModel.save() disabled in -fake mode.")
        else:
            # self.magentaprint("BaseModel.save(str(args), str(kwargs))")
            super().save(*args, **kwargs)

    def magentaprint(text):
        comm.ConsoleHandler.newConsoleHandler().magenta()
        #curtime = datetime.now().time().strftime("%H:%M:%S.%f")
        #output = str(curtime[:len(curtime)-5] + "   | " + str(text))
        #print(output)
        #print(datetime.now().time().strftime("%H:%M:%S.%f")[:-4] + "   | " + str(text)) # two decimal poits
        #print("{0}   | {1}".format(\
        print("{0}: {1}".format(\
            datetime.now().time().strftime("%H:%M:%S.%f")[:-4], # two decimal poits
            text)) 
        comm.ConsoleHandler.newConsoleHandler().white()
