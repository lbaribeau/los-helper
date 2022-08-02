
from command.CommandThatRemovesFromInventory import CommandThatRemovesFromInventory
from comm import RegexStore as R
from misc_functions import magentaprint

class Arm(CommandThatRemovesFromInventory):
    cooldown_after_success = 0
    cooldown_after_failure = 0

    def __init__(self, character, telnetHandler, inventory):
        self.character = character
        self.already_wielding_error = False
        super().__init__(telnetHandler, inventory)

    def notify(self, r, m):
        if r in R.weapon_broken:
            # self.character.inventory  # unset usable perhaps
            self.broken_error = True
            item = self.character.inventory.get(self._sent_target)
            if item:
                # item.set_unusable()
                item.usable = False
        elif r in R.already_wielding + R.already_seconding:
            self.already_wielding_error = True
        super().notify(r, m)

    def execute(self, arg):
        self.broken_error = False
        self.already_wielding_error = False
        super().execute(arg)

class Wield(Arm):
    command = 'wie'
    success_regexes = [
        R.you_wield
    ]
    failure_regexes = [
        R.weapon_broken, 
        # R.cannot_second, 
        R.not_skilled
    ]
    error_regexes = [
        R.dont_have, 
        R.not_weapon, 
        R.already_wielding
    ]
    # def __init__(self, character, telnetHandler, inventory):
    #     self.character=character # How about not referring to character
    #     super().__init__(telnetHandler, inventory)
    #     # self.second = Second(character, telnetHandler) # Better get this as an argument so it can be subscribed

    def notify(self, r, m):
        if r in R.you_wield:
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
    success_regexes = [
        R.off_hand
    ]
    failure_regexes = [
        R.weapon_broken, 
        R.no_primary, 
        R.remove_shield, 
        R.cannot_second,
        R.primary_excludes,
        R.not_skilled,
        R.not_ranger
    ]
    error_regexes = [
        R.dont_have, 
        R.not_weapon, 
        R.already_seconding
    ]
    def notify(self, r, m):
        if r in R.off_hand:
            magentaprint('Second notified, setting weapon2.')
            self.character.weapon2 = m.group('weapon')
        # elif r in R.already_seconding:
        #     self.already_seconding_error = True
        super().notify(r,m)

    # def execute(self, arg):
    #     self.already_seconding_error = False
    #     super().execute(arg)
