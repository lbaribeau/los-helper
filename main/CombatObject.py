
from threading import Thread
import re
from time import time

from misc_functions import magentaprint
from Command import Command
import RegexStore

class CombatObject(object):
    numbers = "(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th|16th|17th|18th|19th)" 
    end_combat_regexes = [
        "Your attack overwhelms (?:the (" + numbers + " )?)?(.+?) and (s?he|it) collapses!",
        "(:?The ?(" + numbers + " )?)?(.+?) flees to the (.+?)\."
    ]

    def __init__(self, telnetHandler):   
        self.telnetHandler = telnetHandler
        self.regexes.extend(self.end_combat_regexes)

    def notify(self, regex, M_obj):
        if regex in self.end_combat_regexes:
            magentaprint(str(self) + " ending combat.")
            self.stop()


class CombatObject2(CombatObject):
    # SmartCombat, Kill, and Cast
    # (Well, not SmartCombat...)
    target = None  
    thread = None
    stopping = False
      
    @classmethod
    def stop(cls):
        cls.stopping = True

    @classmethod
    def keep_going(cls):
        magentaprint(str(cls) + " keep_going " + str(cls.stopping))
        
        if cls.stopping is True:
            cls.stopping = False

    @classmethod
    def engage(cls, telnetHandler, target=None):
        if target:
            cls.target = target
            cls.stopping = False
            # That needs to handle existing threads

        if cls.thread is None or not cls.thread.is_alive():
            # not is_alive() means it won't look at stopping anymore so we're good.
            cls.thread = Thread(target = cls.run, args = (telnetHandler, target))
            cls.thread.start()
        # else:
            # Well the other thread CAN stil be sleeping from a kill error.  (ie misspelled target)
            # That puts it into a 3 second sleep, then the timer gets corrected 0.3s after.
            # So.... maybe it must poll fast... or we need signals... do we use that thread or a new thread??
            # Maybe we write its code smarter to handle this case... don't sleep till after the cooldown's verified

    def start_thread(self, target=None):
        self.engage(self.telnetHandler, target)


class SimpleCombatObject(CombatObject2, Command):
    # This is for code used by Kill and Cast but not SmartCombat

    def __init__(self, telnetHandler):
        self.end_combat_regexes.extend(self.error_regexes)
        CombatObject.__init__(self, telnetHandler)
        Command.__init__(self, telnetHandler)
        # Commented: done in 'Command'
        # self.regexes.extend(self.success_regexes)
        # self.regexes.extend(self.failure_regexes)

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


class Cast(SimpleCombatObject):
    command = 'cas'  # This gets rewritten to append the spellname alot
    cooldown_after_success = 4  # Gets rewritten by characterClass...
    cooldown_after_failure = 0
    regexes = []  

    aura_regex = r"You glow with a (.+?) aura\."
    success_regexes = [  
        r"You cast a (.+?) spell on (.+?)\.",
        r"(.+?) spell cast\.",
        r"You cast a (.+?) spell\.",
        aura_regex
    ]

    failure_regexes = [  
        # This is a unique case because the cooldown afterwards depends on the spell
        r"Your spell fails\.",
        r"You cannot meet the casting cost!"
    ]   

    error_regexes = [
        r"That spell does not exist\.",
        r"You don't know that spell\.",
        r"Spell name is not unique\.",
        r"Cast what\?",
        r"They are not here\.",
        r"Cast at whom\?" 
    ]

    aura = None
    aura_timer = 0
    aura_refresh = 480

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
        if regex is self.aura_regex:
            self.__class__.aura = M_obj.group(1)
            self.__class__.aura_timer = time()
        super().notify(regex, M_obj)

    def notify_failure(self, regex, M_obj):
        spell = self.command.split(' ')[1].lower()
        if re.match("vig?|vigor?", spell) or \
           re.match("show-?|show-au?|show-aura?", spell) or \
           re.match("lig?|light?", spell) or \
           re.match("me?|mend?|mend-w?|mend-wou?|mend-wound?|mend-wounds", spell):
            self.clear_timer()

    def cast(self, spell, target=None):
        self.__class__.command = "cas " + spell
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

    def spam_spell(self, character, spell, target=None):  # Maybe a prompt object would be better than character
        spell_cost = 2 if re.match("vig?|vigor?", spell) else \
                     1 if re.match("show?|show-a?|show-aura?", spell) else \
                     5 if re.match("lig?|light?", spell) else 3

        self.result = ''

        while self.result != 'success' and character.MANA >= spell_cost:
            self.wait_until_ready()
            self.cast(spell, target)
            self.wait_for_flag()


class Kill(SimpleCombatObject):
    command = 'k'
    cooldown_after_success = 3
    cooldown_after_failure = 3 
    regexes = [] 

    def notify(self, regex, M_obj):
        if regex in RegexStore.hastened:
            Kill.cooldown_after_success = 2  
        elif regex in RegexStore.feel_slower:
            Kill.cooldown_after_success = 3
            # Erhm... do we want to start a thread to get the timing exact... (todo)
        super().notify(regex, M_obj)

    error_regexes = [
        r"You don't see that here\.",
        r"Attack what\?"
    ]

    # This might be a performance problem.
    success_regexes = [
        "You swing with your .+?, hacking (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\.",
        "You slice (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage with your .+?\.",
        "You slash at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) and hit for \d+ damage\.",

        "You chop at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\.",
        "You stab (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) with your .+?, causing \d+ damage",
        "You lunge at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), striking for \d+ damage\.",

        "You lash out and thump (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\.",
        "You punch (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\.",
        "You kick (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\.",
        "You head-butt (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\.",
        "You grab (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) and gouge (him|her|it) for \d+ damage\.",

        "You smash your .+? into (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), causing \d+ damage\.",
        "You heave your .+? at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), smashing (him|her|it) for \d+ damage\.",
        "You bludgeon (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\.",

        "You lunge at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), hitting them for \d+ damage\.",
        "You swing your .+?, striking for \d+ damage\.",
        "You sweep (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) with your .+? for \d+ damage\.",

        "Your missile slams into (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\.",
        "You attack (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) with your .+?, striking for \d+ damage\.",
        "You use your .+? to strike (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) for \d+ damage\."
    ]

    failure_regexes = [
        "You hack with your .+?, but your blow swings wide of the mark\.",
        "You slice your .+? at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but miss\.",
        "You slash at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but miss\.",

        "You chop at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) but fail to hit them\.",
        "You try to stab (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) with your .+?, but miss\.",
        "You lunge wildly at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) but mistime the strike\.",

        "You lash out at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but miss\.",
        "You swing a wild punch at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but it misses\.",
        "You kick at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but fail to hurt them\.",
        "You grab at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but (s?he|it) escapes your grasp\.",
        "You try to gouge (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but can't get a good grip\.",

        "You swing your .+? at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but miss\.",
        "You heave your .+? in a wide arc, but fail to hit anything\.",
        "You try to bludgeon (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but miss\.",

        "You lunge at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but you miss\.",
        "Your .+? swings, but fails to connect\.",
        "You sweep at (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) with your .+?, but miss\.",

        "Your missile arcs towards (:the )?(" + SimpleCombatObject.numbers + " )?(.+?), but fails to hit them\.",
        "You attack (:the )?(" + SimpleCombatObject.numbers + " )?(.+?) with your .+?, but miss\.",
        "You use your .+?, but nothing hits (:the )?(" + SimpleCombatObject.numbers + " )?(.+?)\."
    ]
