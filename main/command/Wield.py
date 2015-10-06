
from command.Command import Command
from comm import RegexStore
from misc_functions import magentaprint

class Wield(Command):
    command = 'wie'
    cooldown_after_success = 0.75
    cooldown_after_failure = 0.75
    success_regexes = [RegexStore.you_wield] 
    failure_regexes = [RegexStore.wield_broken] 
    error_regexes = [RegexStore.dont_have, RegexStore.not_weapon]

    def __init__(self, character, telnetHandler):
        self.character = character
        self.end_thread_regexes = self.error_regexes
        super().__init__(telnetHandler)

    def notify(self, r, m):
        if r in RegexStore.you_wield:
            self.character.weapon1 = m.group(1)
        elif r in RegexStore.wield_broken:
            crash
        super().notify(r, m)

    # success, failure, error booleans
