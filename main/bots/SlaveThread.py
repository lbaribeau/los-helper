from hashlib import new
import random

from misc_functions import *
from bots.BotThread import *
from db.Database import *
from db.MudMap import *
from reactions.HealSlaveReactions import HealSlaveReactions
from reactions.KillSlaveReactions import KillSlaveReactions

class SlaveThread(BotThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None, master_name="", kill=False):
        super().__init__(character, command_handler, mud_reader_handler, mud_map)

        self.slave_state = SlaveState()
        self.heal_slave_reactions = HealSlaveReactions(mud_reader_handler, command_handler, master_name, self.cast, character, self.slave_state)
        self.last_action = get_timeint()

        # if kill:
        #     self.kill_slave_reactions = KillSlaveReactions(mud_reader_handler, command_handler, master_name)

    def stop(self):
        super().stop()

    def decide_where_to_go(self):
        while True:
            self.command_handler.user_ca('think')
            self.sleep(60)
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

class SlaveState(object):
    def __init__(self):
        self.targets = []
    
    def add_target_to_state(self, target):
        self.targets.append({"name": target, "last_buff": 0, "needs_heal": True})

    def find_or_add_target(self, name):
        for target in self.targets:
            if name == target.name:
                return target
        return self.add_target_to_state(target)
    
    def update_target_buff(self, name, buff_state):
        for target in self.targets:
            if name == target.name:
                target.last_buff = get_timeint()

    def update_target_heal(self, name, heal_state):
        for target in self.targets:
            if name == target.name:
                target.needs_heal = heal_state
    
    @staticmethod
    def target_needs_buff(target):
        return (get_timeint() - target.last_buff) > 60