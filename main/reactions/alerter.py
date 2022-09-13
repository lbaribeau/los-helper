
from comm import RegexStore as R
from misc_functions import magentaprint

class Alerter(object):
    ''' This thing makes a noise when your character gets to full HP/MP'''
    on_off = False

    def __init__(self, prompt, info):
        self.info       = info
        self.prompt     = prompt
        self.alert_flag = True # This part is a latch so we only alert once
        self.regex_cart = [
            R.prompt
        ]
        self.num_ticks  = 0

    def notify(self, regex, M_obj):
        if not self.on_off:
            return
        # if not hasattr(self.char, 'info'):
        #     return

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
        if (self.prompt.hp < self.info.maxHP or
            self.prompt.mp < self.info.maxMP):
            self.alert_flag = False
        else:
            if self.alert_flag:
                return
            else:
                self.alert_flag = True
                print('\a')

