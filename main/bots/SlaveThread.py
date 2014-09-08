import random

from misc_functions import *
from BotThread import *
from Database import *
from MudMap import *

class SlaveThread(BotThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                inventory=None, mud_map=None, master_name=""):
        super(SlaveThread, self).__init__(character, command_handler, mud_reader_handler, inventory, mud_map)

    def stop(self):
        super(SlaveThread, self).stop()

    def decide_where_to_go(self):
        #must do an action every 30 seconds or so to avoid timing out
        #perhaps an emote or something custom like emote "grovels at $master" when the master is around
        #and "curses $master" when he's away
        return #not implemented

    def follow_master(self):
        return

    def find_master(self):
        return #not implemented
