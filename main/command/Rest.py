
import time

from comm import RegexStore as R
from misc_functions import magentaprint
from command.Command import Command

class Rest(Command):
    # Not finished
    command='rest'
    def __init__(self, telnet_handler):
        self.hp_amount = None
        self.mp_amount = None
        self.success_regexes = [R.rest]
        self.failure_regexes = [] # Needed? Can rest fail?
        self.error_regexes = []
        # Would be good to have failure... 
        super().__init__(telnet_handler)
        # self.regex_cart = [
        #     # R.rest,  # TODO: add resting regexes
        #     R.you_feel_the_benefits
        # ]
        self.regex_cart.append(R.you_feel_the_benefits)

    def notify(self, regex, M_obj):
        if regex in R.rest:
            magentaprint("Rest(Command) notify() you were able to rest")
        if regex in R.you_feel_the_benefits:
            magentaprint("Rest(Command) notify() you_feel_the_benefits")
        super().notify(regex, M_obj)

# You stop resting.

# import statistics
# import R
# import time

# class Prompt(object):
#     # I think this is the wrong one... I think this is a 1st draft and a "Prompt" object got done elsewhere

#     first_tick = None
#     tick_times = []
#     tick_periods = []

#     def __init__(self, character):
#         self.alert_flag = True
#         self.character = character
#         self.regex_cart = [R.prompt]
#         self.num_ticks = 0

#     def notify(self, regex, M_obj):
#         self.prev_hp = self.character.HEALTH
#         self.prev_mp = self.character.MANA

#         self.character.HEALTH = int(M_obj.group(1))
#         self.character.MANA = int(M_obj.group(2))

#         if not hasattr(self.character, 'maxHP'):
#             return

#         self.maybe_alert()

#         if self.prev_hp < self.character.HEALTH and self.prev_mp < self.character.MANA:
#             self.do_tick()

#     def maybe_alert(self):
#         if self.character.HEALTH == self.character.maxHP and \
#            self.character.MANA == self.character.maxMP and \
#            not self.alert_flag:
#             self.alert_flag = True
#             print('\a')
#         else:
#             if self.character.HEALTH < self.character.maxHP or \
#                self.character.MANA < self.character.maxMP:
#                 self.alert_flag = False

#     def do_tick(self):
#         # if not self.__class__.first_tick:
#         #     self.__class__.first_tick = time.time()
#         # else:
#         #     self.__class__.tick_times.append(time.time() - len(self.__class__.tick_times))
#         self.__class__.tick_times.append(time.time())
#         num_ticks = len(self.__class__.tick_times)

#         if num_ticks > 1:
#             self.__class__.tick_periods.append(self.__class__.tick_times[num_ticks-1] - self.__class__.tick_times[num_ticks-2])

#         # if self.__class__.tick_times:
#            #  self.__class__.tick_times.append(time.time() - self.__class__)
#         # else:

#     @classmethod
#     def tick_period(cls):
#         return round(sum(cls.tick_periods) / len(cls.tick_periods), 1) 

#     def tick_period2(self):
#         return 

#     @classmethod 
#     def next_tick(cls):
#         pass
