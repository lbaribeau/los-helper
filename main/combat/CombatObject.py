
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
        self.end_combat_regexes = [RegexStore.mob_died, RegexStore.mob_fled, RegexStore.you_died]
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
            # magentaprint(str(self) + " ending combat.")
            # Need to add check to make sure it was the mob that fled.
            self.stop()

    @property
    def end_combat(self):
        return self.result in RegexStore.mob_died or self.result in RegexStore.mob_fled or self.result in RegexStore.you_died

    @property
    def mob_died(self):
        return self.result in chain.from_iterable(RegexStore.mob_died)
    @property
    def mob_fled(self):
        return self.result in chain.from_iterable(RegexStore.mob_fled)

    def in_combat(self):
        magentaprint(str(self) + " in combat returning " + str(hasattr(self, 'thread') and self.thread and self.thread.is_alive()))
        return hasattr(self, 'thread') and self.thread and self.thread.is_alive()

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
        # magentaprint('SimpleCombatObject r ' + regex + ' errors ' + str(self.error_regexes))
        # if regex in chain.from_iterable(self.error_regexes):
        #     self.stop()

    @property
    def end_combat(self):
        return super().end_combat or self.result in chain.from_iterable(self.error_regexes)

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

