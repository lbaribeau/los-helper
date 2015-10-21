
from command.Command import Command
from comm import RegexStore
from misc_functions import magentaprint

class Arm(Command):
    cooldown_after_success = 0
    cooldown_after_failure = 0

    def __init__(self, character, telnetHandler):
        self.character = character
        self.already_wielding_error = False
        super().__init__(telnetHandler)

    def notify(self, r, m):
        if r in RegexStore.wield_broken:
            # self.character.inventory  # set is_unusable perhaps
            self.broken_error = True
        elif r in RegexStore.already_wielding or r in RegexStore.already_seconding:
            self.already_wielding_error = True
        super().notify(r, m)

    def execute(self, arg):
        self.broken_error = False
        self.already_wielding_error = False
        super().execute(arg)

class Wield(Arm):
    command = 'wie'
    success_regexes = [RegexStore.you_wield] 
    failure_regexes = [RegexStore.wield_broken, RegexStore.cannot_second, RegexStore.not_skilled] 
    error_regexes = [RegexStore.dont_have, RegexStore.not_weapon, RegexStore.already_wielding]

    def __init__(self, character, telnetHandler):
        super().__init__(character, telnetHandler)
        self.second = Second(character, telnetHandler)

    def notify(self, r, m):
        if r in RegexStore.you_wield:
            if m.group('weapon').endswith('in your off hand'):
                return
            self.character.weapon1 = m.group('weapon')
        super().notify(r, m)

    # success, failure, error booleans

    def execute(self, arg):
        self.already_wielding_error = False
        super().execute(arg)

    # def second(self, arg):
    #     self.second.
    #     self.command = 'seco'
    #     self.execute(arg)

class Second(Arm):
    command = 'seco'
    success_regexes = [RegexStore.off_hand] 
    failure_regexes = [RegexStore.wield_broken, RegexStore.no_primary, RegexStore.remove_shield, RegexStore.cannot_second, \
                       RegexStore.primary_excludes, RegexStore.not_skilled, RegexStore.not_ranger] 
    error_regexes = [RegexStore.dont_have, RegexStore.not_weapon, RegexStore.already_seconding]

    def notify(self, r, m):
        if r in RegexStore.off_hand:
            magentaprint('Second notified, setting weapon2.')
            self.character.weapon2 = m.group('weapon')
        # elif r in RegexStore.already_seconding:
        #     self.already_seconding_error = True
        super().notify(r,m)

    # def execute(self, arg):
    #     self.already_seconding_error = False
    #     super().execute(arg)
