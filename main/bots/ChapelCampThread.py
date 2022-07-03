import random

from misc_functions import *
from bots.BotThread import *
from db.Database import *
from db.MudMap import *
from reactions.HealSlaveReactions import HealSlaveReactions
from reactions.KillSlaveReactions import KillSlaveReactions

class ChapelCampThread(BotThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None):
        super().__init__(character, command_handler, mud_reader_handler, mud_map)

        self.heal_slave_reactions = HealSlaveReactions(mud_reader_handler, command_handler, master_name)


    # Vigor spell cast on Aerp.
    # It appears to have no effect!

    def stop(self):
        super().stop()

    def decide_where_to_go(self):
        while True:
            self.command_handler.user_ca('rest')
            self.sleep(60)
        return #not implemented

    def do_post_go_actions(self):
        return

    def follow_master(self):
        return

    def find_master(self):
        return #not implemented
