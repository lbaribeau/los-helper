
#import statistics
import time

from comm import RegexStore
from misc_functions import magentaprint
from combat.Cast import Cast

class HealthMonitor(object):
    def __init__(self, character):
        self.char = character
        self.regex_cart = [RegexStore.prompt]

        # first_tick      = None
        self.tick_times   = []
        self.tick_periods = []
        self.hpticks      = []
        self.mpticks      = [] # How to determine chapel ticks... maybe with character's area id
        self.rest_hpticks = []
        self.rest_mpticks = []
        self.vig_amounts  = []
        self.mend_amounts = []

    def notify(self, regex, M_obj):
        if self.hp_delta() > 0 and self.mp_delta() > 0:
            if M_obj.group(3):
                self.do_rest()
            else:
                self.do_tick()
        elif self.hp_delta() > 0 and self.mp_delta() < 0:
            # Better not to rely on cast command... use mp amount and hp/mp deltas
            # if Cast.command.split(' ')[1].startswith('v'):
            # elif Cast.command.split(' ')[1].startswith('m'):
            if self.mp_delta() == -Cast.vig_amount:
                self.do_vig()
            elif self.mp_delta() == -Cast.mend_amount:
                self.do_mend()
            else:
                magentaprint("HealthMonitor: weird mana decrease and health increase.")
        elif self.hp_delta() < 0:
            self.do_mob_hit()

    def do_rest(self):
        if not self.hp_maxed():
            self.rest_hpticks.append(self.hp_delta())
        if not self.mp_maxed():
            self.rest_mpticks.append(self.mp_delta())

    def do_tick(self):
        if not self.hp_maxed():
            self.hpticks.append(self.hp_delta())
        if not self.mp_maxed():
            self.mpticks.append(self.mp_delta())

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
            self.vig_amounts.append(self.hp_delta())

    def do_mend(self):
        if not self.hp_maxed():
            self.mend_amounts.append(self.hp_delta())

    def do_mob_hit(self):
        # Mobs object seems to handle this
        pass

    def hp_delta(self):
        return self.char.prompt.hp_delta()
    def mp_delta(self):
        return self.char.prompt.mp_delta()
    def hp_maxed(self):
        return self.char.prompt.hp == self.char.info.maxHP
    def mp_maxed(self):
        return self.char.prompt.mp == self.char.info.maxMP
    def tick_period(self):
        return round(sum(self.tick_periods) / len(self.tick_periods), 1) 
    def tick_period2(self):
        return 
    def next_tick(self):
        pass
