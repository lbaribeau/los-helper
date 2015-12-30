
from comm import RegexStore
from misc_functions import magentaprint

class Prompt(object):
    def __init__(self):
        self.regex_cart = [RegexStore.prompt]
        self.hp = 100
        self.mp = 100
        self.prev_hp = 100
        self.prev_mp = 100
        
    def notify(self, regex, M_obj):
        # Maybe we want hp/mp deltas clumped (prev_hp == hp on black magic cast...)
        if int(M_obj.group(1)) != self.hp or int(M_obj.group(2)) != self.mp:
            self.prev_hp = self.hp
            self.hp = int(M_obj.group(1))
            self.prev_mp = self.mp
            self.mp = int(M_obj.group(2))

        # self.prev_hp = self.hp if int(M_obj.group(1)) != self.hp else self.prev_hp
        # self.prev_mp = self.mp if int(M_obj.group(2)) != self.mp else self.prev_mp
        # self.hp = int(M_obj.group(1))
        # self.mp = int(M_obj.group(2))

    def hp_delta(self):
        return self.hp - self.prev_hp
    def mp_delta(self):
        return self.mp - self.prev_mp
