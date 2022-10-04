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
        self.target = None
        self.action_cooldown = 60
        self.heal_cooldown = 20
        self.buff_cooldown = 120

        # if kill:
        #     self.kill_slave_reactions = KillSlaveReactions(mud_reader_handler, command_handler, master_name)

    def stop(self):
        super().stop()

    def check_cooldown(self, last_use, seconds):
        should_do_thing = False
        now = get_timeint()
        seconds_since_last_buff = (now - last_use).total_seconds()
        if seconds_since_last_buff > seconds:
            should_do_thing = True
        else:
            should_do_thing = False
        
        return should_do_thing

    def check_healslave_cooldown(self, target, cooldown_key, req_mana, seconds):
        should_do_thing = False
        if self.character.MANA > req_mana:
            last_use = target[cooldown_key]
            should_do_thing = self.check_cooldown(last_use, seconds)
        
        if should_do_thing:
            self.target[cooldown_key] = get_timeint()
            magentaprint("Setting updating target with this key right now:" + cooldown_key, False)

        return should_do_thing

    def cast_spell(self, target_name, spell):
        self.last_action = get_timeint()
        self.cast.cast(spell, target_name)
        time.sleep(4)

    def should_buff_target(self, target):
        last_use_key = "last_buff"
        mana_requirement = 24        
        return self.check_healslave_cooldown(target, last_use_key, mana_requirement, self.buff_cooldown)

    def should_heal_target(self, target, mana_requirement):
        last_use_key = "last_heal"
        should_heal = self.check_healslave_cooldown(target, last_use_key, mana_requirement, self.heal_cooldown)

        return should_heal
    
    def heal_target(self, target, big_heal=True):
        if big_heal and self.should_heal_target(target, 4):
            self.cast_spell(target.name, "mend")
        elif not big_heal and self.character.MANA > 1:
            self.cast_spell(target.name, "vigor")
        else:
            magentaprint("target already healed or I can't cast recently so no go", False)

    def buff_target(self, target):
        if self.should_buff_target(target):
            self.cast_spell(target.name, "bless")
            self.cast_spell(target.name, "protection")
        else:
            magentaprint("target already buffed recently so no go", False)

    def do_heal_routine(self, target):
        self.buff_target(target)
        magentaprint("should start healing " + target.name, False)
        self.heal_target(target)

    def decide_where_to_go(self):
        while True:
            self.check_for_new_target()
            self.sleep(1)
            if self.check_cooldown(self.last_action, self.action_cooldown):
                self.command_handler.user_ca("rest")
        return #not implemented

    def check_for_new_target(self):
        for target in self.slave_state.targets:
            if target["needs_buff"]:
                target["needs_buff"] = False
                self.do_heal_routine(target)
            elif target["needs_heal"]:
                target["needs_heal"] = False
                self.heal_target(target, big_heal=False)

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
        self.targets.append({"name": target, "last_buff": 0, "last_heal": 0, "needs_buff": False, "needs_heal": False})

    def find_or_add_target(self, name):
        for target in self.targets:
            if name == target.name:
                return target
        return self.add_target_to_state(target)

    # def update_target_buff(self, name, buff_state):
    #     for target in self.targets:
    #         if name == target.name:
    #             target.last_buff = get_timeint()

    # def update_target_heal(self, name, heal_state):
    #     for target in self.targets:
    #         if name == target.name:
    #             target.needs_heal = heal_state
    
    # @staticmethod
    # def target_needs_buff(target):
    #     return (get_timeint() - target.last_buff) > 60