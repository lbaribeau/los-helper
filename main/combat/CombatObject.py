
from threading import Thread
import re
from time import time
from itertools import chain

from combat.ThreadingMixin import ThreadingMixin
from command.Command import Command
from misc_functions import magentaprint
from comm import RegexStore

class CombatObject(object):
    def __init__(self, telnetHandler):   
        self.end_combat_regexes = [RegexStore.mob_died, RegexStore.mob_fled]
        self.telnetHandler = telnetHandler
        # self.regexes.extend(self.end_combat_regexes)
        # self.regex_cart = [RegexStore.mob_died, RegexStore.mob_fled]
        # if hasattr(self, regex_cart):
        #     self.regex_cart.extend([RegexStore.mob_died, RegexStore.mob_fled])
        # else:
        #     self.regex_cart = [RegexStore.mob_died, RegexStore.mob_fled]
        # self.regex_cart.extend([RegexStore.mob_died, RegexStore.mob_fled])
        # self.regexes = self.end_combat_regexes
        self.regex_cart = self.end_combat_regexes[:]

    def notify(self, regex, M_obj):
        self.result = regex
        if self.end_combat:
            magentaprint(str(self) + " ending combat.")
            self.stop()

    @property 
    def end_combat(self):
        # magentaprint("CombatObject.end_combat")
        # # magentaprint(str(self))
        # magentaprint(str(self.result))
        return self.result in RegexStore.mob_died or self.result in RegexStore.mob_fled

    @property
    def mob_died(self):
        return self.result in chain.from_iterable(RegexStore.mob_died)
    @property
    def mob_fled(self):
        return self.result in chain.from_iterable(RegexStore.mob_fled)

class SimpleCombatObject(CombatObject, ThreadingMixin, Command):
    # This is for code used by Kill and Cast but not SmartCombat
    timer = time() - 10

    def __init__(self, telnetHandler):
        Command.__init__(self, telnetHandler)
        # CombatObject2.__init__(self, telnetHandler)
        ## Commented: done in 'Command'
        ## self.regexes.extend(self.success_regexes)
        ## self.regexes.extend(self.failure_regexes)
        # self.regexes.extend(self.end_combat_regexes)
        ## self.regex_cart.extend([RegexStore.mob_died, RegexStore.mob_fled]))
        # magentaprint("SimpleCombatObject end_combat_regexes: " + str(self.end_combat_regexes))
        # self.regex_cart.extend([RegexStore.mob_died, RegexStore.mob_fled].extend(self.end_combat_regexes))
        self.end_combat_regexes = [RegexStore.mob_died, RegexStore.mob_fled]
        self.regex_cart.extend(self.end_combat_regexes)
        self.end_combat_regexes.extend(self.error_regexes)
        # magentaprint("SimepleCombatObject end_combat_regexes: " + str(self.end_combat_regexes))

    def notify(self, regex, M_obj):
        magentaprint(str(self) + " notified.")
        CombatObject.notify(self, regex, M_obj)
        Command.notify(self, regex, M_obj)

    # def execute(self, target):
    #     # self.wait_until_ready()
    #     if not self.stopping:
    #         super().execute(target)

    # Needs to be a class method because the human doesn't have the object.
    @classmethod
    def run(cls, telnetHandler, target=None):
        # magentaprint(str(telnetHandler))
        cls.stopping = False
        cls.target = target
        cls.wait_until_ready()

        while not cls.stopping:
            cls.send(telnetHandler, cls.target)
            # cls.wait_until_ready()  # Too early
            # Just wait_for_flag should do the trick.
            # The sleep amount is verified after that.
            cls.wait_for_class_flag()
            cls.wait_until_ready()

        magentaprint(str(cls) + " ending run." )
