
from comm import RegexStore
from misc_functions import magentaprint

class Alerter(object):
    def __init__(self, character):
        self.char = character
        self.alert_flag = True
        self.regex_cart = [RegexStore.prompt]
        self.num_ticks = 0

    def notify(self, regex, M_obj):
        return # Turned off sound
        if not hasattr(self.char, 'info'):
            return

        if self.char.prompt.hp == self.char.info.maxHP and self.char.prompt.mp == self.char.info.maxMP and not self.alert_flag:
            self.alert_flag = True
            print('\a')
        else:
            if self.char.prompt.hp < self.char.info.maxHP or self.char.prompt.mp < self.char.info.maxMP:
                self.alert_flag = False
