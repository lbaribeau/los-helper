# This thread is used to time retries for cool abilities (haste, pray, berserk, etc.).  
# Construct it with a CoolAbility.
  
from misc_functions import *
from BotReactions import *
import atexit 
import time

from misc_functions import *

class SkillTimer():
    def __init__(self, regex, set_timer_to=0, func_pointer=None):
        self.regex = regex
        self.set_timer_to = set_timer_to
        self.func_pointer = func_pointer

class ClassSkillReaction(BotReaction):
    def __init__(self, mud_reader_handler, command, success_timer, fail_timer, end_timer=SkillTimer("NEVERMATCHEVER~")):
        self.command = command
        self.success_timer = success_timer
        self.fail_timer = fail_timer
        self.end_timer = end_timer
        self.timer = 0
        self.last_used = 0

        self.regexes = [self.success_timer.regex,
                        self.fail_timer.regex,
                        self.end_timer.regex]

        self.mud_reader_handler = mud_reader_handler    
        self.mud_reader_handler.register_reaction(self)

    def __iter__(self):
        return self
    
    def next(self): # Python 3: def __next__(self)
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1
    
    def notify(self, regex, M_obj):
        if regex == self.success_timer.regex:
            self.timer = self.success_timer.set_timer_to
            #doFunction
        elif regex is self.fail_timer.regex:
            self.timer = self.fail_timer.set_timer_to
        elif regex is self.end_timer.regex:
            self.timer = 0
            #doFunction