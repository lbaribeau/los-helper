
import re
import time
from itertools import chain

from command.Command import Command
from comm import RegexStore
from misc_functions import magentaprint
from combat.Kill import Kill
from combat.Cast import Cast

class Go(Command):
    command = 'go'
    success_regexes = [RegexStore.area, RegexStore.too_dark]
    error_regexes = [RegexStore.no_exit, RegexStore.go_where]
    failure_regexes = [
        RegexStore.blocked_path, RegexStore.cant_go, RegexStore.open_first,
        RegexStore.class_prohibited, RegexStore.level_too_low, RegexStore.level_too_high, RegexStore.not_invited,
        RegexStore.not_open_during_day, RegexStore.not_open_during_night, RegexStore.no_items_allowed,
        RegexStore.locked, RegexStore.no_right, RegexStore.in_tune,
        RegexStore.not_authorized, RegexStore.cannot_force, RegexStore.washroom, RegexStore.cliff
    ]
    cooldown_after_success = 0.34
    good_mud_timeout = 20.0
        # There's a rancher gate node that seems to take quite a while

    def __init__(self, telnetHandler, character):
        super().__init__(telnetHandler)
        self.open = Open(telnetHandler)
        self.regex_cart.append(RegexStore.mob_fled)
        self.character = character

    def wait_for_flag(self):
        # magentaprint("Go.wait_for_flag()")
        self.cartography.__class__._waiter_flag = False
        # self.__class__._waiter_flag = False
        super().wait_for_flag()
        if not self.cartography.__class__._waiter_flag:
            self.cartography.wait_for_flag()

    def notify(self, regex, M_obj):
        magentaprint("Go notified.")
        if regex in RegexStore.open_first:
            self.door = True
        # elif regex in chain.from_iterable(self.success_regexes) and not self.__class__._waiter_flag:
        #     self.character.mobs.list.reset()
        #     self.character.mobs.attacking.reset()
        #     # time.sleep(0.8)  # Hacked fix to get_heal_path being called before Cartography updates area_id
        super().notify(regex, M_obj)

    def execute(self, target):
        # magentaprint("Go.execute()")
        self.door = False
        # while self.character.TRYING_TO_MOVE is True:
        #     # Hack - wait for Cartography
        #     time.sleep(0.05)

        # if self.character.TRYING_TO_MOVE:
        #     self.cartography.wait_for_flag()

        self.character.TRYING_TO_MOVE = True
        magentaprint("Go.execute() " + target)
        super().execute(target)

    def persistent_execute(self, target):
        super().persistent_execute(target)
        if self.door:
            self.open.execute(target)
            self.open.wait_for_flag()
            if self.open.success:
                super().persistent_execute(target)

    @classmethod
    def compose_command(cls, target=None):
        if not target:
            magentaprint("Go where?")
            return ""
        elif cls.is_direction(target):
            return target
        else:
            return cls.command + " " + target

    @classmethod
    def is_direction(cls, s):
        return s.strip() in ['n', 's', 'e', 'w', 'nw', 'ne', 'se', 'sw'] or re.match('up?$', s) or \
               re.match('(do?|down?)$', s) or re.match('out?$', s)

    @classmethod
    def wait_until_ready(cls):
        super().wait_until_ready()
        Cast.wait_until_ready()
        Kill.wait_until_ready()

class Open(Command):
    command = 'open'
    success_regexes = [RegexStore.already_open, RegexStore.open_success]
    error_regexes = [RegexStore.no_exit, RegexStore.open_what]
    failure_regexes = [RegexStore.locked]

    def notify(self, r, m):
        magentaprint("Open notified.")
        super().notify(r, m)

