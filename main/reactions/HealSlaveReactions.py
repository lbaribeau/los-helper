
from reactions.BotReactions import BotReaction
from misc_functions import *

class HealSlaveReactions(BotReaction):
    def __init__(self, mudReaderHandler, command_handler, master, cast, character, slave_state):
        #[Group] Twerp took 4 combat damage
        self.group_damage = "\[Group\] {0} took ([\d]*) combat damage".format(master)
        self.heal_trigger = "^(.+?) decides to take a rest."
        self.heal_continue = "You gain (?:\d+?) experience.\n?\r?.+? spell cast on (.+?)\."
        self.heal_stop = "^.+? spell cast on (.+?).\n?\r?It appears to have no effect!"
        self.target_not_here = "They are not here\."

        magentaprint("slave started for <" + master + ">", False)
        if master == "camp":
            magentaprint("camp mode started", False)
            self.regexes = [self.heal_trigger, self.heal_continue, self.heal_stop, self.target_not_here]
        else:
            self.regexes = [self.group_damage]

        self.master = master
        self.dmg = 0

        self.character = character
        self.slave_state = slave_state
        self.command_handler = command_handler
        self.mudReaderHandler = mudReaderHandler
        self.cast = cast
        self.target = ""
        self.known_targets = {}
        
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def check_healslave_cooldown(self, buff_key, req_mana, seconds):
        should_do_thing = False
        if self.character.MANA > req_mana:
            if buff_key in self.known_targets.keys() and self.known_targets[buff_key] is not None:
                last_buff_time = self.known_targets[buff_key]
                now = get_timeint()
                seconds_since_last_buff = (now - last_buff_time).total_seconds()
                if seconds_since_last_buff > seconds:
                    should_do_thing = True
            else:
                should_do_thing = True
        
        if should_do_thing:
            self.known_targets[buff_key] = get_timeint()
            magentaprint("Setting updating target with this key right now:" + buff_key, False)

        return should_do_thing

    def cast_spell(self, spell):
        self.cast.cast(spell, self.target)
        time.sleep(4)

    def should_buff_target(self):
        buff_key = self.target + "_buff"
        mana_requirement = 24        
        cooldown_in_seconds = 60
        return self.check_healslave_cooldown(buff_key, mana_requirement, cooldown_in_seconds)

    def should_heal_target(self, mana_requirement):
        buff_key = self.target + "_heal"
        cooldown_in_seconds = 20
        return self.check_healslave_cooldown(buff_key, mana_requirement, cooldown_in_seconds)
    
    def heal_target(self):
        if self.should_heal_target(4):
            self.cast_spell("mend")
        elif self.should_heal_target(1):
            self.cast_spell("vigor")
        else:
            magentaprint("target already healed or I can't cast recently so no go", False)

    def buff_target(self):
        if self.should_buff_target():
            self.cast_spell("bless")
            self.cast_spell("protection")
            self.cast_spell("light")
        else:
            magentaprint("target already buffed recently so no go", False)

    def notify(self, regex, M_obj):
        magentaprint(regex, False)
        if regex == self.heal_trigger:
            self.target = M_obj.group(1)
            self.buff_target()
            magentaprint("should start healing " + self.target, False)
            self.heal_target()
        elif regex == self.heal_continue:
            self.target = M_obj.group(1)
            magentaprint("should continue healing " + self.target, False)
            if self.character.MANA > 1:
                self.cast_spell("vigor")
        elif regex == self.heal_stop:
            self.command_handler.process("rest")
        elif regex == self.target_not_here:
            self.target = ""
        elif regex == self.group_damage:
            self.dmg += int(M_obj.group(1))

            magentaprint("{0} {1}".format(self.dmg, self.master), False)
            if (self.dmg >= 10):
                self.dmg = 0
                magentaprint("Notified <" + self.master + ">", False)
                self.cast.process('c vig ' + self.master)
