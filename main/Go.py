
import re

from misc_functions import magentaprint
import RegexStore
from Command import Command

class Go(Command):
    command = 'go'
    success_regexes = [RegexStore.obvious_exits]
    error_regexes = [RegexStore.no_exit, RegexStore.go_where]
    failure_regexes = [
        RegexStore.blocked_path, RegexStore.cant_go, RegexStore.open_first,
        RegexStore.class_prohibited, RegexStore.level_too_low, RegexStore.not_invited,
        RegexStore.not_open_during_day, RegexStore.not_open_during_night, RegexStore.no_items_allowed, 
        RegexStore.locked, RegexStore.no_right, RegexStore.in_tune,
        RegexStore.not_authorized, RegexStore.cannot_force
    ]
    cooldown_after_success = 0.34

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)
        self.open = Open(telnetHandler)

    def notify(self, regex, M_obj):
        super().notify(regex, M_obj)
        if regex is RegexStore.open_first:
            self.door = True

    def execute(self, target):
        self.door = False
        super().execute(target)

    def super_execute(self, target):
        super().super_execute(target)
        if self.door:
            self.open.execute(target)
            self.open.wait_for_flag()
            if self.open.result is 'success':
                super().super_execute(target)

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

class Open(Command):
    command = 'open'
    # success_regexes = [RegexStore]
    success_regexes = [RegexStore.already_open, RegexStore.open_success]
    error_regexes = [RegexStore.no_exit, RegexStore.open_what]
    failure_regexes = [RegexStore.locked]

