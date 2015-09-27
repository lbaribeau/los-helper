
# import statistics

import time

from combat.Cast import Cast
from comm import RegexStore
from misc_functions import magentaprint

class Prompt(object):
    def __init__(self, character):
        self.alert_flag = True
        self.character = character
        self.regex_cart = [RegexStore.prompt]
        self.num_ticks = 0

        # first_tick = None
        self.tick_times = []
        self.tick_periods = []
        self.hpticks = []  
        self.mpticks = []  # How to determine chapel ticks
        self.rest_hpticks = []
        self.rest_mpticks = []
        self.vig_amounts = []
        self.mend_amounts = []

    def notify(self, regex, M_obj):
        self.prev_hp = self.character.HEALTH
        self.prev_mp = self.character.MANA

        self.character.HEALTH = int(M_obj.group(1))
        self.character.MANA = int(M_obj.group(2))

        if not hasattr(self.character, 'maxHP'):
            return

        self.alert_if_maxed()

        if self.prev_hp < self.character.HEALTH and self.prev_mp < self.character.MANA:
            if M_obj.group(3):
                self.do_rest()
            else:
                self.do_tick()
        elif self.prev_hp < self.character.HEALTH and self.prev_mp > self.character.MANA:
            if Cast.command.split(' ')[1].startswith('v'):
                self.do_vig()
            elif Cast.command.split(' ')[1].startswith('m'):
                self.do_mend()
            else:
                magentaprint("Prompt: weirdo situation - mana decrease and health increase.")

    def alert_if_maxed(self):
        if self.character.HEALTH == self.character.maxHP and \
           self.character.MANA == self.character.maxMP and \
           not self.alert_flag:
            self.alert_flag = True
            print('\a')
        else:
            if self.character.HEALTH < self.character.maxHP or \
               self.character.MANA < self.character.maxMP:
                self.alert_flag = False

    def do_rest(self):
        if not self.hp_maxed():
            self.rest_hpticks.append(self.character.HEALTH - self.prev_hp)
        if not self.mp_maxed():
            self.rest_mpticks.append(self.character.MANA - self.prev_mp)

    def do_tick(self):
        if not self.hp_maxed():
            self.hpticks.append(self.character.HEALTH - self.prev_hp)
        if not self.mp_maxed():
            self.mpticks.append(self.character.MANA - self.prev_mp)

        # if not self.__class__.first_tick:
        #     self.__class__.first_tick = time.time()
        # else:
        #     self.__class__.tick_times.append(time.time() - len(self.__class__.tick_times))
        self.tick_times.append(time.time())
        num_ticks = len(self.tick_times)

        if num_ticks > 1:
            self.tick_periods.append(self.tick_times[num_ticks-1] - self.tick_times[num_ticks-2])

    def do_vig(self):
        if not self.hp_maxed():
            self.vig_amounts.append(self.character.HEALTH - self.prev_hp)
    def do_mend(self):
        if not self.hp_maxed():
            self.mend_amounts.append(self.character.HEALTH - self.prev_hp)
    def hp_maxed(self):
        return self.character.HEALTH == self.character.maxHP
    def mp_maxed(self):
        return self.character.MANA == self.character.maxMP
    def max_vigor(self):
        if self.vig_amounts:
            return max(self.vig_amounts)
        else:
            return self.character.pty / 2.3  
    def max_mend(self):
        if self.mend_amounts:
            return max(self.mend_amounts)
        else:
            return 9

        # if self.__class__.tick_times:
	       #  self.__class__.tick_times.append(time.time() - self.__class__)
        # else:

    def tick_period(self):
        return round(sum(self.tick_periods) / len(self.tick_periods), 1) 

    def tick_period2(self):
        return 

    def next_tick(self):
        pass
