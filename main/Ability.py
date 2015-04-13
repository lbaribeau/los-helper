
import time

from Command import Command
from BotReactions import BotReactionWithFlag
import RegexStore

class Ability(Command):
    regexes = []

# class BuffAbility(AbilityWithFailure):
class BuffAbility(Ability):
    active = False

    # @property 
    # def already_buffed_regex(self):
    #     raise NotImplementedError()
    # @property 
    # def wear_off_regex(self):
    #     raise NotImplementedError() 

    def __init__(self, telnetHandler):
        self.thread = None
        super().__init__(telnetHandler)

    def notify(self, regex, M_obj):
        if regex in self.success_regexes:
            self.active = True
        elif regex is self.wear_off_regex:
            self.active = False
        # elif regex is self.already_buffed_regex:
        #     if self.up():
        #         # Timer is completely wrong -> Just set it very high and wait for wear_off_regex
        #         magentaprint("BuffAbility timer was way off.")
        super().notify(regex, M_obj)

    def execute_until_success(self):
        pass

    def stop_executing(self):
        pass

class FastCombatAbility(Ability):  
    # You can attack immediately after these abilities
    # FastTargetedAbility is another possible name
    pass  # We're just using this for a kind of 'typing' for the smartCombat logic

class CombatAbility(Ability):
    # Bash, Circle, Touch, Wither
    def execute(self, target=None):
        Kill.start_timer()
        super().execute(target)
        # self.character.ATTACK_CLK = time()
        # Hmmm.... do abilities need to be constructed with a cooldowns object?
        # How about botThread takes care of that...


# Hint: the 'time' command in game tells you how much time is left on your buff
# Although I don't think I will use the 'lasts' variable.

# I could save a lot of data collection time by parsing the 
# 'time' output and filling in the cooldown info that way.

class Haste(BuffAbility):
# haste = BuffAbility()
    command = "haste"
    cooldown_after_success = 600  # can flee
    cooldown_after_failure = 10  # can flee
    # success_regexes = [r"You feel yourself moving faster\."]
    success_regexes = RegexStore.hastened
    failure_regexes = [r"Your attempt to hasten failed\."]
    already_buffed_regex = "You're already hastened\."
    # wear_off_regex = "You feel slower\."
    wear_off_regex = RegexStore.feel_slower
    lasts = 150
    # self.classes = ["Ran"]
    level = 1

class Pray(BuffAbility):
    command = "pray"
    cooldown_after_success = 610
    cooldown_after_failure = 10  # can flee
    success_regexes = [r"You feel extremely pious\."]
    failure_regexes = [r"Your prayers were not answered\."]
    already_buffed_regex = "You've already prayed\."
    wear_off_regex = "You feel less pious\."
    lasts = 310
    # self.classes = ["Cle", "Pal"]
    level = 1
        # I would do lasts 305 and cooldown 600 but I can't test that right now
   
class Barkskin(BuffAbility):
    command = "barkskin" 
    cooldown_after_success = 600  # can flee, confirmed 10 minutes
    cooldown_after_failure = 10  # can flee
    success_regexes = [r"You feel your skin thickening and hardening\."]
    failure_regexes = [r"Your attempt to invoke barkskin failed\."]
    already_buffed_regex = "Your skin is already hardened\."
    wear_off_regex = "Your skin softens\."
    lasts = 120
    # classes = ["Dru"]
    level = 1

class Berserk(BuffAbility):
    command = "berserk"
    cooldown_after_success = 600
    cooldown_after_failure = 20 
    success_regexes = [r"A red mist coats your vision, your heart pounds harder \. \. \."]
    failure_regexes = [r"You fail to work yourself into a frenzy\."]
    wear_off_regex = "The red mist fades from your sight\."  # Neato dark blue colored text
    lasts = 60
    # classes = ["Bar", "Dar"]
    level = 1

class HealAbility(object):
    pass
    # @property 
    # def max_amount(self):
    #     raise NotImplementedError()

class Meditate(HealAbility, Ability):
    command = "meditate"
    cooldown_after_success = 120
    cooldown_after_failure = 5
    max_amount = 26 #guess
    success_regexes = [r"You feel at one with universe\."]
    failure_regexes = [r"Your spirit is not at peace\."]
    # classes = ["Mon"]
    level = 4

    def set_level(self, level):
        self.max_amount = 18 + level

class AestersTears(HealAbility, Ability):
    command = "sing ae"
    cooldown_after_success = 140  # Can flee/move/attack immediately
    max_amount = 16  # guessed
    success_regexes = ["Your music rejuvenates everyone in the room\."]  # This seems to overwrite Ability...
    # self.failure_regex = "(?!x)x"  # Regex that never matches - Aester never fails
    failure_regexes = []
    # classes = ["Brd"]
    level = 4

# danceOfTheCobra = FastCombatAbility(telnetHandler):
class DanceOfTheCobra(FastCombatAbility):
    command = "sing dance"  # needs target
    cooldown_after_success = 570  # can hit right away i believe
    cooldown_after_failure = 30  # can flee/move/attack
    # success_regex = r"The Dance of the Snake ends\.\n\rYou complete the ritual by touching the (.+?) and the charming takes effect\.\.\."
    success_regexes = [r"he Dance of the Snake ends"]
    # failure_regex = r"The Dance of the Snake has no effect on the (.+?)\.\r\n"  # and you can hit right away.
    failure_regexes = [r"he Dance of the Snake has "]
    # classes = ["Brd"]
    level = 1  # guessed
    # magentaprint("Dance of the Cobra regexes before calling super: " + str(self.regexes))
    # The mob just stops attacking, so how about turning off casting and just attacking him to death.
    # You can attack immediately after on success or fail.
    # But if you attacked then you have to wait to use it.

class Turn(FastCombatAbility):
    command = "turn"  # needs target
    cooldown_after_success = 30  # can attack immediately, but flee/move is 3 seconds later
    cooldown_after_failure = 30  # can attack immediately, but flee/move is 3 seconds later
                                 # (Said Please wait 1 sec THEN Please wait 2 sec)
    success_regexes = [r"You turned the (.+?) for (.+?) damage\."  ]
    failure_regexes = [r"You failed to turn the (.+?)\."]
    # classes = ["Cle", "Pal"]
    level = 1

    # TODO: needs work:
    valid_targets = ["zombie", "skeleton", "ghast", "poltergeist", "geist", "ghoul"]

class Touch(CombatAbility):
    command = "touch"
    cooldown_after_success = 270
    cooldown_after_failure = 270
    success_regexes = [r"You touched the (.+?) for (.+?) damage\."]
    failure_regexes = [r"You failed to harm the (.+?)\."]
    # classes = ["Mon"]
    level = 4

class Wither(CombatAbility):
    command = "wither"
    cooldown_after_success = 300  # Guessed out of the blue
    cooldown_after_failure = 10  # can't attack/flee/move immediately
    success_regexes = [r" the (.+?) for (.+?) damage\."]  # TODO: Obviously needs work
    failure_regexes = [r"Your withering touch did not hurt the (\.?)\."]
    # classes = ["Dar"]
    level = 1

class Bash(CombatAbility):
    command = "bash"
    cooldown_after_success = 3
    cooldown_after_failure = 3
    success_regexes = [r"You bash the (.+?), confusing them\."]
    failure_regexes = [r"You failed to bash it\."]
    # classes = ["Bar", "Fig"]
    level = 1

class Circle(CombatAbility):
    command = "ci"
    cooldown_after_success = 3
    cooldown_after_failure = 3
    success_regexes = [r"You circle the (.+?)\."]
    failure_regexes = [r"You failed to circle it\."]
    # classes = ["Bar", "Fig"]
    level = 1

# class Hide(object):
# class Backstab(object):
# class Steal(object):


# Wither interrupts flee.
# I hope I can assume that casting is on a completely different clock.
# I think combat abilities have a 3 sec flee cooldown, success or fail.
# Dance and turn are fast for flee/attack/move.

# BuffAbilities could be in another file.

# This should be a few files... but I'm not too sure how to split it up.  
# It's a lot of scrolling right now.


# class AbilityWithTarget(AbilityWithFailure):

#     _command = NotImplementedError()

#     def use(self, target):
#         try:
#             self.command = self._command + " " + target
#         except AttributeError:
#             magentaprint("Why?????")
#             magentaprint(self._command)
#             magentaprint(target)
#             # if self.command != None:
#             #     magentaprint(self.command)
#             self.command = "Yay!"
#         super(AbilityWithTarget, self).use()
#         self.cooldowns.ATTACK_CLK = time()

#     def use_wait(self, target):
#         self.use(target)
#         self.wait_for_flag()

# @property is causing me issues... Like, one ability got a success_regex from another ability,
# as if success_regex was a static thing for all different instances.  It also wouldn't let me 
# overwrite self.command.










# Previous attempt
# from Command import Command

# class Ability(Command):
#     pass

# class BuffAbility(Ability):
#     active = False

#     # @property 
#     # def already_buffed_regex(self):
#     #     raise NotImplementedError()
#     # @property 
#     # def wear_off_regex(self):
#     #     raise NotImplementedError() 

#     def notify(self, regex, M_obj):
#         if regex is self.success_regex:
#             self.active = True
#         elif regex is self.wear_off_regex:
#             self.active = False

#         super().notify(regex, M_obj)

# class FastCombatAbility(Ability):  
#     # You can attack immediately after these abilities
#     # FastTargetedAbility is another possible name
#     pass

# class CombatAbility(Ability):
#     # Bash, Circle, Touch, Wither
#     def execute(self, target=None):
#         Kill.start_timer()
#         super().execute(target)
#         # self.character.ATTACK_CLK = time()
#         # Hmmm.... do abilities need to be constructed with a cooldowns object?
#         # How about botThread takes care of that...

# class HealAbility(object):
#     pass

# class AestersTears(HealAbility, Ability):
#     command = "sing ae"
#     cooldown_after_success = 140  # Can flee/move/attack immediately
#     max_amount = 16  # guessed
#     success_regexes = ["Your music rejuvenates everyone in the room\."]  # This seems to overwrite Ability...
#     failure_regexes = ["(?!x)x"]  # Regex that never matches - Aester never fails
#     # classes = ["Brd"]
#     level = 4
#     regexes = []

# class DanceOfTheCobra(FastCombatAbility):
#     command = 'sin da '
#     cooldown_after_success = 570
#     cooldown_after_failure = 10
#     success_regexes = [r"he Dance of the Snake ends"]
#     # failure_regex = r"The Dance of the Snake has no effect on the (.+?)\.\r\n"  # and you can hit right away.
#     failure_regexes = [r"he Dance of the Snake has "]
#     # classes = ["Brd"]
#     level = 1  # guessed
#     # magentaprint("Dance of the Cobra regexes before calling super: " + str(self.regexes))
#     # regexes = []
#     # super().__init__(telnetHandler)    
#     regexes = []

# import time

# from BotReactions import BotReactionWithFlag
# from misc_functions import magentaprint

# from CombatObject import Ability

# class Ability(BotReactionWithFlag):
#     ''' Abilites are things like haste, barkskin, berserk, 
#     pray (buffs,) meditate, sing (heals,) wither, 
#     turn (damage,) circle, bash, touch, backstab, and steal (combat.) 
#     The combat abilities change KillThread timing.  

#     They are organized this way to facilite their usage in BotThread.

#     There are some special cases.  Pray is used uniquely (before resting, 
#     while other buffs are used after resting or before combat,) and turn 
#     can be used only on undead.  The combat abilities share a cooldown 
#     with normal attacks.
#     '''

#     # regexes = []

#     def __init__(self, mudReaderHandler, telnetHandler):
#         super(Ability, self).__init__()
#         magentaprint("Init for Ability " + str(self))
#         self.telnetHandler = telnetHandler
#         self.timer = time.time()  # gives the time when the ability is available
#           # timer will have to be adjusted to be checked on login
#         self.success = False  # check this value to see if use() was successful
#         # self.regexes.append(self.success_regex)  # Hmmm
#         self.regexes.append(self.success_regex)
#         magentaprint(self.regexes)
#         magentaprint("That is the final regexes before registering.")
#            # Needs to work when AbilityWithFlag calls it
#            # and also when for instances of Ability.
#         mudReaderHandler.register_reaction(self)
#         # super(Ability, self).__init__(self.regexes)

#     # @property
#     # def command(self): 
#     #     raise NotImplementedError()
#     # @property
#     # def cooldown_after_success(self): 
#     #     raise NotImplementedError()
#     # @property
#     # def success_regex(self):
#     #     raise NotImplementedError()

#     def notify(self, regex, M_obj):
#         if regex is self.success_regex:
#             self.success = True

#         magentaprint("Notify on Ablity was called.")

#         super(Ability, self).notify(regex, M_obj)

#     def use(self, target=""):
#         if self.timer - time.time() < 0.75:
#             magentaprint("Ability.use: sleeping " + str(self.timer - time.time()))
#             time.sleep(max(0, self.timer - time.time()))
#         else:
#             magentaprint("Ability: not ready for " + self.timer - time.time() + " seconds.")
#             return

#         self.success = False
#         # magentaprint("Ability: Calling telnetHandler.write(" + self.command + " " + target + ")")
#         self.telnetHandler.write(self.command + " " + target)
#         self.timer = time.time() + self.cooldown_after_success

#     def use_wait(self, target=""):
#         self.use(target)
#         self.wait_for_flag()

#     def up(self):
#         return self.timer < time.time()

#     #def use_until_successful(self):
#     # This will be done by AbilityThread
#     # Maybe this can start a Ability thread

# class AbilityWithFailure(Ability):
#     # Some abilities never fail (sing aester,) but most do (buff abilities, meditate)
#     # @property
#     # def cooldown_after_failure(self): 
#     #     raise NotImplementedError()
#     # @property
#     # def failure_regex(self):
#     #     raise NotImplementedError()

#     def __init__(self, mudReaderHandler, telnetHandler):
#         magentaprint("Init for AbilityWithFailure " + str(self))
#         # regexes = [self.failure_regex]
#         self.regexes.append(self.failure_regex)
#         magentaprint("...regexes: " + str(self.regexes))
#         super(AbilityWithFailure, self).__init__(mudReaderHandler, telnetHandler)

#     def notify(self, regex, M_obj):
#         if regex is self.failure_regex:
#             self.timer = self.timer - self.cooldown_after_success + self.cooldown_after_failure

#         super(AbilityWithFailure, self).notify(regex, M_obj)
