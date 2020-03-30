
from db.Database import *
from db.MudMap import MudMap

class DatabaseHandler(object):
    def __init__(self, map):
        self.map = map
        create_tables()
        db.close()

    def get_smithy_paths(self):
        return self.map.get_smithy_paths
