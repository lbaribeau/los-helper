import random

from misc_functions import *
from bots.BotThread import *
from db.Database import *
from db.MudMap import *
from reactions.HealSlaveReactions import HealSlaveReactions

class SlaveThread(BotThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                inventory=None, mud_map=None, master_name=""):
        super(SlaveThread, self).__init__(character, command_handler, mud_reader_handler, inventory, mud_map)

        self.heal_slave_reactions = HealSlaveReactions(mud_reader_handler, command_handler)

    def stop(self):
        super(SlaveThread, self).stop()

    def decide_where_to_go(self):
        while(True):
            self.commandHandler.user_ca('smile')
            self.sleep(10)
        #must do an action every 30 seconds or so to avoid timing out
        #perhaps an emote or something custom like emote "grovels at $master" when the master is around
        #and "curses $master" when he's away
        return #not implemented

    def do_post_go_actions(self):
        return

    def follow_master(self):
        return

    def find_master(self):
        return #not implemented
