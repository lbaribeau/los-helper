
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

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)
        self.open = Open(telnetHandler)

    def notify(self, regex, M_obj):
        super().notify(regex, M_obj)
        if regex is RegexStore.open_first:
            self.door = True

    def execute(self, target):
        self.door = False
        super.execute(target)

    def super_execute(self, target):
        super().super_execute()
        if self.door:
            self.open.execute(target)
            self.open.wait_for_flag()
            if self.open.result is 'success':
                super().super_execute()

class Open(Command):
    command = 'open'
    # success_regexes = [RegexStore]
    success_regexes = [RegexStore.already_open, RegexStore.open_success]
    error_regexes = [RegexStore.no_exit, RegexStore.open_what]
    failure_regexes = [RegexStore.locked]

