
import sys, time
import random

from db.Database import *
from db.MudMap import *
from db.MudArea import *
from fake.FakeTelnetSocket import FakeTelnetSocket

class FakeTelnetHandler(object):
    def __init__(self):
        self.mud_map = MudMap()
        self.tn = self.connect_to_MUD()
        self.tn.connect()

        self.echoing = True

    def write(self, command):
        if self.echoing:
            magentaprint('{' + command + '}',False)

        self.tn.write(command)

    def connect_to_MUD(self):
        return FakeTelnetSocket(self.mud_map) 

    def close(self):
        self.tn.close()

    def get_socket(self):
        return self.tn.get_socket()

    def read_some(self):
        s=self.tn.read_some()
        # magentaprint("FakeTelnetHandler read_some() got {0}".format(s))
        # return self.tn.read_some()
        return s

