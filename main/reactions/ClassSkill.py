# This thread is used to time retries for cool abilities (haste, pray, berserk, etc.).  
# Construct it with a CoolAbility.
  
from misc_functions import *
from reactions.BotReactions import *
import atexit 
import time

from misc_functions import *

class SkillTimer():
    def __init__(self, regex, set_timer_to=0, func_pointer=None):
        self.regex = regex
        self.set_timer_to = set_timer_to
        self.func_pointer = func_pointer

    def __int__(self):
        return int(self.set_timer_to)

class ClassSkillReaction(BotReaction):
    def __init__(self, mud_reader_handler, command, success_timer, fail_timer, end_timer=SkillTimer("NEVERMATCHEVER~")):
        self.command = command
        self.success_timer = success_timer
        self.fail_timer = fail_timer
        self.end_timer = end_timer
        self.timer = 0
        self.last_used = 0

        self.timer_check = "(" + command + ")[\s]*(?:(\*READY\*)|(?:(?:([\d]*):)?0?([\d]*) (?:minutes|seconds?) (?:remaining|left on current run)))"
        # self.please_wait = "Please wait (?:([\d]*):)?([\d]*) more (?:minutes|seconds?)\."
        self.regexes = [self.timer_check,
                        self.success_timer.regex,
                        self.fail_timer.regex,
                        self.end_timer.regex]

        self.mud_reader_handler = mud_reader_handler    
        self.mud_reader_handler.register_reaction(self)
    
    def notify(self, regex, M_obj):
        if regex == self.success_timer.regex:
            self.timer = self.success_timer.set_timer_to
            #doFunction
        elif regex is self.fail_timer.regex:
            self.timer = self.fail_timer.set_timer_to
        elif regex is self.end_timer.regex:
            self.timer = self.end_timer.set_timer_to
            #doFunction
        elif regex is self.timer_check:
            command = M_obj.group(1).strip()
            ready = M_obj.group(2)
            minutes = M_obj.group(3)
            seconds = M_obj.group(4)

            # magentaprint(command, False)
            # magentaprint(ready, False)
            # magentaprint(minutes, False)
            # magentaprint(seconds, False)

            if command == self.command:
                if ready is not None:
                    #magentaprint(command + " is ready.",False)
                    self.timer = 0 #*READY*
                elif minutes is None and seconds is not None:
                    #magentaprint(command + " is ready in '" + str(seconds) + "' seconds.",False)
                    self.timer = int(seconds)
                    self.last_used = time.time() + self.timer
                else:
                    #magentaprint(command + " is ready in '" + str(minutes) + "' minutes " + str(seconds) + "' seconds.",False)
                    self.timer = (int(minutes) * 60) + int(seconds)
                    self.last_used = time.time() + self.timer

                # magentaprint(self.timer, False)
                # magentaprint("Skill ready in: " + str(self.last_used - time.time()), False)

    def can_use(self):
        cooldown = time.time() - self.last_used

        if self.timer < cooldown:
            return True

        return False

        #magentaprint("Timer set to: " + str(self.timer) + " by " + regex, False)

