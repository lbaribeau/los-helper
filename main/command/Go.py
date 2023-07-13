
import re
import time
from itertools import chain

from command.Command import Command
from comm import RegexStore as R
from misc_functions import magentaprint
from combat.Kill import Kill
from combat.Cast import Cast

class Go(Command):
    command = 'go'
    success_regexes = [
        R.area, 
        R.too_dark
    ]
    error_regexes = [
        R.no_exit, 
        R.go_where
    ]
    failure_regexes = [
        R.blocked_path,          
        R.cant_go,       
        R.open_first,
        R.class_prohibited,      
        R.level_too_low, 
        R.level_too_high, 
        R.not_invited,
        R.not_open_during_day,   
        R.locked,        
        R.no_items_allowed,
        R.not_open_during_night, 
        R.no_right,      
        R.in_tune,
        R.not_authorized,        
        R.cannot_force,  
        R.washroom, 
        R.cliff, # Why does this timeout?
        R.occupied_area # Does cartography need to know this one? Unlikely
    ]
    cooldown_after_success = 0.34
    good_mud_timeout = 20.0
        # There's a rancher gate node that seems to take quite a while

    def __init__(self, kill, cast, telnetHandler, character):
        super().__init__(telnetHandler)
        self.open = Open(telnetHandler)
        self.kill = kill
        self.cast = cast
        self.character = character
        self.regex_cart.append(R.mob_fled)

    def wait_for_flag(self, **kwargs):
        # magentaprint("Go.wait_for_flag()")
        self.cartography.__class__._waiter_flag = False
        # self.cartography.clear() # Should be called on execute
        # self.__class__._waiter_flag = False
        super().wait_for_flag(**kwargs)
        # if not self.cartography.__class__._waiter_flag:
        #     self.cartography.wait_for_flag()
        self.cartography.wait_for_flag(**kwargs)

    def notify(self, regex, M_obj):
        magentaprint("Go notified.")
        if regex in R.open_first:
            self.door = True
        # elif regex in chain.from_iterable(self.success_regexes) and not self.__class__._waiter_flag:
        #     self.character.mobs.list.reset()
        #     self.character.mobs.attacking.reset()
        #     # time.sleep(0.8)  # Hacked fix to get_heal_path being called before Cartography updates area_id
        # Maybe also wait for cartography? Our wait function waits for cartography
        super().notify(regex, M_obj)

    def execute(self, target):
        self.door = False
        self.character.LAST_DIRECTION = target
        # while self.character.TRYING_TO_MOVE is True:
        #     # Hack - wait for Cartography
        #     time.sleep(0.05)

        # if self.character.TRYING_TO_MOVE:
        #     self.cartography.wait_for_flag()

        self.character.TRYING_TO_MOVE = True
        self.wait_for_flag(timeout=3) # also waits for cartography
        # self.cartography.wait_for_flag(timeout=3)
        self.cartography.clear()
        magentaprint("Go.execute() 2")
        super().execute(target) # self.clear()

    def persistent_execute(self, target):
        super().persistent_execute(target)
        if self.door:
            self.open.execute_and_wait(target)
            # self.open.wait_for_flag()
            if self.open.success:
                super().persistent_execute(target)

    # @classmethod
    def compose_command(self, target=None):
        if not target:
            magentaprint("Go where?")
            return #self.command
        elif self.is_direction(target):
            return target # ie. 's' or 'nw' (no need for the 'go' part of the command)
        else:
            return self.command + " " + target

    @classmethod
    def is_direction(cls, s):
        return s.strip() in ['n', 's', 'e', 'w', 'nw', 'ne', 'se', 'sw'] or re.match('up?$', s) or \
               re.match('(do?|down?)$', s) or re.match('out?$', s)

    # @classmethod
    def wait_until_ready(self):
        super().wait_until_ready()
        self.cast.wait_until_ready()
        self.kill.wait_until_ready()

    @property
    def blocked(self):
        # This is for mobs blocking you
        return self.result in R.blocked_path

    def wait_execute_and_wait(self, exit):
        self.wait_until_ready()
        self.execute_and_wait(exit)  #super().execute_and_wait(target=None)

class Open(Command):
    command = 'open'
    success_regexes = [R.already_open, R.open_success]
    error_regexes   = [R.no_exit,      R.open_what]
    failure_regexes = [R.locked]

    def notify(self, r, m):
        magentaprint("Open notified.")
        super().notify(r, m)

