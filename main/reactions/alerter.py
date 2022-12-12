
from comm import RegexStore as R
from misc_functions import magentaprint

class Alerter(object):
    ''' This thing can make a noise when your character gets to full or low HP/MP'''
    def __init__(self, prompt, info):
        self.info       = info
        self.prompt     = prompt
        self.alert_flag = True 
        # alert_flag is a latch so we only alert once; True means ready, False means ok don't alarm again
        self.regex_cart = [
            R.prompt
        ]
        self.on = True

    def notify(self, regex, M_obj):
        if not self.on or not hasattr(self, 'info'):
            return

        self.alert_if_low_hp()
        self.unset_latch_at_70_percent()

    def alert_if_low_hp(self):
        if self.prompt.hp < 0.35*self.info.maxHP and self.alert_flag:
            self.alert_flag = False
            print('\a') 

    def unset_latch_at_70_percent(self):
        if self.prompt.hp > 0.7*self.info.maxHP:
            self.alert_flag = True

    def alert_if_maxed(self):
        if (self.prompt.hp < self.info.maxHP or self.prompt.mp < self.info.maxMP):
            self.alert_flag = True
        else:
            if self.alert_flag:
                self.alert_flag = False
                print('\a')

        # C = self.char
        # if (C.prompt.hp == C.info.maxHP and 
        #     C.prompt.mp == C.info.maxMP and 
        #     not self.alert_flag):
        #     self.alert_flag = True
        #     print('\a')
        # else:
        #     if (C.prompt.hp < C.info.maxHP or 
        #         C.prompt.mp < C.info.maxMP):
        #         self.alert_flag = False
