
from threading import Thread
import re
from time import time
# from itertools import chaa
import itertools

from misc_functions import magentaprint
from Command import Command
import RegexStore
from ThreadingMixin import ThreadingMixin

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
        if regex in itertools.chain.from_iterable(self.end_combat_regexes):
            magentaprint(str(self) + " ending combat.")
            self.stop()

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
        CombatObject.notify(self, regex, M_obj)
        Command.notify(self, regex, M_obj)

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

class Kill(SimpleCombatObject):
    command = 'k'
    cooldown_after_success = 3
    cooldown_after_failure = 3 
    regexes = [] 

    good_MUD_timeout = 1.5  # Kill regexes are complicated and you don't want to fail too badly during combat.

    success_regexes = [RegexStore.attack_hit]
    failure_regexes = [RegexStore.attack_miss]
    error_regexes = [RegexStore.attack_error]

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)
        self.regex_cart.extend([RegexStore.hastened, RegexStore.already_hastened, RegexStore.feel_slower])

    def notify(self, regex, M_obj):
        if regex in RegexStore.hastened or regex in RegexStore.already_hastened:
            Kill.cooldown_after_success = 2  
            Kill.cooldown_after_failure = 2  
        elif regex in RegexStore.feel_slower:
            Kill.cooldown_after_success = 3
            Kill.cooldown_after_failure = 3  
            # Erhm... do we want to start a thread to get the timing exact... (todo)
        super().notify(regex, M_obj)


class Cast(SimpleCombatObject):
    command = 'c'  # This gets rewritten to append the spellname alot
    cooldown_after_success = 4  # Gets rewritten by characterClass...
    cooldown_after_failure = 0
    regexes = []  

    success_regexes = [RegexStore.cast, RegexStore.aura]
    failure_regexes = [RegexStore.cast_failure, RegexStore.no_mana]
    error_regexes = [RegexStore.cast_error]

    aura = None
    aura_timer = 0
    aura_refresh = 480

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)
        self.end_combat_regexes.append(RegexStore.no_mana)

    # Commented... hmmm.. I went with the notify_failure(), I think so I wasn't checking for the regex twice...
    # Just a logic structure thing.
       # def notify(self, regex, M_obj):
       #     if regex is self.spell_failed:
       #         # Looks like we need spell to be instance or class variable
       #         # What is it currently - it's currently part of command I believe...
       #         # does this code even work yet.... command will just get changed...
       #         # ... so we can get spell from command here inevitably...
       #         if re.match("vig?|vigor?", spell):
       #             self.__class__.timer = self.__class__.timer - self.cooldown_after_success + self.cooldown_after_failure
       #         pass
       #     super().notify(regex, M_obj)

    def notify(self, regex, M_obj):
        if regex in RegexStore.aura:
            self.__class__.aura = M_obj.group(1)
            self.__class__.aura_timer = time()
        super().notify(regex, M_obj)

    def notify_failure(self, regex, M_obj):
        spell = self.command.split(' ')[1].lower()
        if re.match("vi?|vigo?|vigor", spell) or \
           re.match("show-?|show-au?|show-aura?", spell) or \
           re.match("lig?|light?", spell) or \
           re.match("me?|mend?|mend-w?|mend-wou?|mend-wound?|mend-wounds", spell):
            self.clear_timer()

    def start_thread(self, spell, target=None):
        self.__class__.command = 'c ' + spell
        super().start_thread(target)

    def cast(self, spell, target=None):
        self.__class__.command = 'c ' + spell
        self.execute(target)
        # self.wait_for_flag()
        # I think I only need to provide waiting calls since other 
        # calls can just be done with telnetHandler
        # Maybe the way to go is @classmethods need not wait (human use,)
        # and calls using the instance will wait.
        # The caller even has access to wait_for_flag so this is not important.

        # Keep in mind that cls.target is for thread use.

    def update_aura(self):
        if time() > self.aura_timer + self.aura_refresh:
            self.cast('show')
            self.wait_for_flag()
        else:
            magentaprint("Last aura update %d seconds ago." % round(time.time() - self.aura_timer))

    def spam_spell(self, character, spell, target=None):  # Maybe a prompt object would be better than character
        spell_cost = 2 if re.match("vig?|vigor?", spell) else \
                     1 if re.match("show?|show-a?|show-aura?", spell) else \
                     5 if re.match("lig?|light?", spell) else 3

        self.result = ''

        while self.result != 'success' and character.MANA >= spell_cost:
            self.wait_until_ready()
            self.cast(spell, target)
            self.wait_for_flag()

