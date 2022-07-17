
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
        
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        magentaprint(regex, False)
        if regex == self.heal_trigger:
            self.target = M_obj.group(1)
            time.sleep(4)
            magentaprint("should start healing " + self.target, False)
            if self.character.MANA > 24:
                self.cast.cast("bless", self.target)
                time.sleep(4)
                self.cast.cast("protection", self.target)
                time.sleep(4)
            if self.character.MANA > 4:
                self.cast.cast("mend", self.target)
            elif self.character.MANA > 1:
                self.cast.cast("vigor", self.target)
        elif regex == self.heal_continue:
            self.target = M_obj.group(1)
            time.sleep(4)
            magentaprint("should continue healing " + self.target, False)
            if self.character.MANA > 1:
                self.cast.cast("vigor", self.target)
        elif regex == self.heal_stop:
            self.command_handler.process("rest")
        elif regex == self.target_not_here:
            self.target = ""
            # self.target
        elif regex == self.group_damage:
            self.dmg += int(M_obj.group(1))

            magentaprint("{0} {1}".format(self.dmg, self.master), False)
            if (self.dmg >= 10):
                self.dmg = 0
                magentaprint("Notified <" + self.master + ">", False)
                self.cast.process('c vig ' + self.master)
