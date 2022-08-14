
from threading import Thread
import re
from time                  import time
import itertools
from combat.ThreadingMixin import ThreadingMixin
from command.Command       import Command
from misc_functions        import magentaprint
from comm                  import RegexStore as R

class CombatObject(ThreadingMixin):
    # SmartCombat, kill, cast
    def __init__(self, telnetHandler):
        # self.end_combat_regexes = [
        #     R.mob_died, 
        #     R.mob_fled, 
        #     R.you_died
        # ]
        self.end_combat_regexes = [
            R.mob_died,
            R.mob_fled,
            R.you_died
        ]
        self.telnetHandler = telnetHandler
        # self.regexes.extend(self.end_combat_regexes)
        # self.regex_cart = [R.mob_died, R.mob_fled]
        # if hasattr(self, regex_cart):
        #     self.regex_cart.extend([R.mob_died, R.mob_fled])
        # else:
        #     self.regex_cart = [R.mob_died, R.mob_fled]
        # self.regex_cart.extend([R.mob_died, R.mob_fled])
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
        return self.result in R.mob_died or self.result in R.mob_fled or self.result in R.you_died
        #return self.result in self.end_combat_regexes
    @property
    def mob_died(self):
        return self.result in itertools.chain.from_iterable(R.mob_died)
    @property
    def mob_fled(self):
        return self.result in itertools.chain.from_iterable(R.mob_fled)
    def in_combat(self):
        magentaprint(str(self) + " in combat returning " + str(hasattr(self, 'thread') and self.thread and self.thread.is_alive()))
        return hasattr(self, 'thread') and self.thread and self.thread.is_alive()

class SimpleCombatObject(CombatObject, Command):
    # This is for code used by Kill and Cast but not SmartCombat
    timer = time() - 10

    def __init__(self, telnetHandler):
        Command.__init__(self, telnetHandler)
        # CombatObject2.__init__(self, telnetHandler)
        ## Commented: done in 'Command'
        ## self.regexes.extend(self.success_regexes)
        ## self.regexes.extend(self.failure_regexes)
        # self.regexes.extend(self.end_combat_regexes)
        ## self.regex_cart.extend([R.mob_died, R.mob_fled]))
        # magentaprint("SimpleCombatObject end_combat_regexes: " + str(self.end_combat_regexes))
        # self.regex_cart.extend([R.mob_died, R.mob_fled].extend(self.end_combat_regexes))
        self.end_combat_regexes = [R.mob_died, R.mob_fled]
        self.regex_cart.extend(self.end_combat_regexes)
        self.end_combat_regexes.extend(self.error_regexes)
        # magentaprint("SimepleCombatObject end_combat_regexes: " + str(self.end_combat_regexes))

    def notify(self, regex, M_obj):
        # magentaprint(str(self) + " notified.")
        CombatObject.notify(self, regex, M_obj)
        Command.notify(self, regex, M_obj)
        # magentaprint('SimpleCombatObject r ' + regex + ' errors ' + str(self.error_regexes))
        # if regex in chain.from_iterable(self.error_regexes):
        #     self.stop()

    @property
    def end_combat(self):
        # magentaprint("SimpleCombatObject.end_combat():\n\tsuper().end_combat: {0}\n\tself.result: {1}\n\tself.error_regexes: {2}\n\tresult in error regexes: {3}".format(
        #     super().end_combat, self.result, self.error_regexes, self.result in itertools.chain.from_iterable(self.error_regexes)))
        magentaprint("SimpleCombatObject.end_combat is {0}".format(super().end_combat or self.result in itertools.chain.from_iterable(self.error_regexes)))
        return super().end_combat or self.result in itertools.chain.from_iterable(self.error_regexes)

    # Needs to be a class method because the human doesn't have the object.
    #@classmethod
    # def run(cls, telnetHandler, target=None):
    #     # magentaprint(str(telnetHandler))
    #     cls.stopping = False
    #     cls.target = target
    #     cls.wait_until_ready()

    #     while not cls.stopping:
    #         cls.send(telnetHandler, cls.target)
    #         # cls.wait_until_ready()  # Too early
    #         # Just wait_for_flag should do the trick.
    #         # The sleep amount is verified after that.
    #         cls.wait_for_class_flag() # So the class flag, is that the command lag flag?
    #         cls.wait_until_ready()

    #     magentaprint(str(cls) + " ending run." )
    # Change back to real object... undo class variable experiment
    def run(self, telnetHandler, target=None):
        # magentaprint(str(telnetHandler))
        self.stopping = False
        self.target = target
        self.wait_until_ready()

        while not self.stopping:
            self.send(telnetHandler, self.target)
            # cls.wait_until_ready()  # Too early
            # Just wait_for_flag should do the trick.
            # The sleep amount is verified after that.
            # (Eh what is going on here)
            self.wait_for_class_flag() # So the class flag, is that the command lag flag?
            # ie. threading.Event.wait()?
            self.wait_until_ready()
            # It's simple - send, wait for the notification, wait the cooldown, repeat

        magentaprint(str(self) + " ending run." )

