from peewee import *
from db.Database import *
from misc_functions import *

class BaseModel(Model):
    def __eq__(self, other): #simple type check
        if type(other) is type(self):
            return True
        else:
            return False

    class Meta:
        database = db

    def to_string(self):
        return str(self.id)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def save(self, *args, **kwargs):
        # Disable saving in -fake environment
        # We don't want the test world to edit the DB

        if '-fake' in sys.argv:
            print("BaseModel.save() disabled in -fake mode.")
            return
        else:
            # print("BaseModel.save")
            # print(str(args))
            super().save(*args, **kwargs)
