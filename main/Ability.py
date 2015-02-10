import time

from BotReactions import BotReactionWithFlag
from misc_functions import magentaprint

class Ability(BotReactionWithFlag):
    ''' Abilites are things like haste, barkskin, berserk, 
    pray (buffs,) meditate, sing (heals,) wither, 
    turn (damage,) circle, bash, touch, backstab, and steal (combat.) 
    The combat abilities change KillThread timing.  

    They are organized this way to facilite their usage in BotThread.

    There are some special cases.  Pray is used uniquely (before resting, 
    while other buffs are used after resting or before combat,) and turn 
    can be used only on undead.  The combat abilities share a cooldown 
    with normal attacks.
    '''

    # regexes = []

    def __init__(self, mudReaderHandler, telnetHandler):
        super(Ability, self).__init__()
        magentaprint("Init for Ability " + str(self))
        self.telnetHandler = telnetHandler
        self.timer = time.time()  # gives the time when the ability is available
          # timer will have to be adjusted to be checked on login
        self.success = False  # check this value to see if use() was successful
        # self.regexes.append(self.success_regex)  # Hmmm
        self.regexes.append(self.success_regex)
        magentaprint(self.regexes)
        magentaprint("That is the final regexes before registering.")
           # Needs to work when AbilityWithFlag calls it
           # and also when for instances of Ability.
        mudReaderHandler.register_reaction(self)
        # super(Ability, self).__init__(self.regexes)

    # @property
    # def command(self): 
    #     raise NotImplementedError()
    # @property
    # def cooldown_after_success(self): 
    #     raise NotImplementedError()
    # @property
    # def success_regex(self):
    #     raise NotImplementedError()

    def notify(self, regex, M_obj):
        if regex is self.success_regex:
            self.success = True

        magentaprint("Notify on Ablity was called.")

        super(Ability, self).notify(regex, M_obj)

    def use(self, target=""):
        if self.timer - time.time() < 0.75:
            magentaprint("Ability.use: sleeping " + str(self.timer - time.time()))
            time.sleep(max(0, self.timer - time.time()))
        else:
            magentaprint("Ability: not ready for " + self.timer - time.time() + " seconds.")
            return

        self.success = False
        # magentaprint("Ability: Calling telnetHandler.write(" + self.command + " " + target + ")")
        self.telnetHandler.write(self.command + " " + target)
        self.timer = time.time() + self.cooldown_after_success

    def use_wait(self, target=""):
        self.use(target)
        self.wait_for_flag()

    def up(self):
        return self.timer < time.time()

    #def use_until_successful(self):
    # This will be done by AbilityThread
    # Maybe this can start a Ability thread

class AbilityWithFailure(Ability):
    # Some abilities never fail (sing aester,) but most do (buff abilities, meditate)
    # @property
    # def cooldown_after_failure(self): 
    #     raise NotImplementedError()
    # @property
    # def failure_regex(self):
    #     raise NotImplementedError()

    def __init__(self, mudReaderHandler, telnetHandler):
        magentaprint("Init for AbilityWithFailure " + str(self))
        # regexes = [self.failure_regex]
        self.regexes.append(self.failure_regex)
        magentaprint("...regexes: " + str(self.regexes))
        super(AbilityWithFailure, self).__init__(mudReaderHandler, telnetHandler)

    def notify(self, regex, M_obj):
        if regex is self.failure_regex:
            self.timer = self.timer - self.cooldown_after_success + self.cooldown_after_failure

        super(AbilityWithFailure, self).notify(regex, M_obj)


class BuffAbility(AbilityWithFailure):
    active = False

    # @property 
    # def already_buffed_regex(self):
    #     raise NotImplementedError()
    # @property 
    # def wear_off_regex(self):
    #     raise NotImplementedError() 

    def notify(self, regex, M_obj):
        if regex is self.success_regex:
            self.active = True
        elif regex is self.wear_off_regex:
            self.active = False

        super(BuffAbility, self).notify(regex, M_obj)


class FastCombatAbility(AbilityWithFailure):  
    # You can attack immediately after these abilities
    # FastTargetedAbility is another possible name
    pass

class CombatAbility(AbilityWithFailure):
    def use(self, target=""):
        super(CombatAbility, self).use(target)
        # self.character.ATTACK_CLK = time()
        # Hmmm.... do abilities need to be constructed with a cooldowns object?
        # How about botThread takes care of that...


# Hint: the 'time' command in game tells you how much time is left on your buff
# Although I don't think I will use the 'lasts' variable.

# I could save a lot of data collection time by parsing the 
# 'time' output and filling in the cooldown info that way.

class Haste(BuffAbility):
# haste = BuffAbility()
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "haste"
        self.cooldown_after_success = 600  # can flee
        self.cooldown_after_failure = 10  # can flee
        self.success_regex = "You feel yourself moving faster\."
        self.failure_regex = "Your attempt to hasten failed\."
        self.already_buffed_regex = "You're already hastened\."
        self.wear_off_regex = "You feel slower\."
        self.lasts = 150
        # self.classes = ["Ran"]
        self.level = 1
        super(Haste, self).__init__(mudReaderHandler, telnetHandler)

class Pray(BuffAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "pray"
        self.cooldown_after_success = 610
        self.cooldown_after_failure = 10  # can flee
        self.success_regex = "You feel extremely pious\."
        self.failure_regex = "Your prayers were not answered\."
        self.already_buffed_regex = "You've already prayed\."
        self.wear_off_regex = "You feel less pious\."
        self.lasts = 310
        # self.classes = ["Cle", "Pal"]
        self.level = 1
        super(Pray, self).__init__(mudReaderHandler, telnetHandler)
        # I would do lasts 305 and cooldown 600 but I can't test that right now
   
class Barkskin(BuffAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "barkskin" 
        self.cooldown_after_success = 600  # can flee, confirmed 10 minutes
        self.cooldown_after_failure = 10  # can flee
        self.success_regex = "You feel your skin thickening and hardening\."
        self.failure_regex = "Your attempt to invoke barkskin failed\."
        self.already_buffed_regex = "Your skin is already hardened\."
        self.wear_off_regex = "Your skin softens\."
        self.lasts = 120
        # classes = ["Dru"]
        self.level = 1
        super(Barkskin, self).__init__(mudReaderHandler, telnetHandler)

class Berserk(BuffAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "berserk"
        self.cooldown_after_success = 600
        self.cooldown_after_failure = 20 
        self.success_regex = "A red mist coats your vision, your heart pounds harder \. \. \."
        failure_regex = "You fail to work yourself into a frenzy\."
        self.wear_off_regex = "The red mist fades from your sight\."  # Neato dark blue colored text
        self.lasts = 60
        # classes = ["Bar", "Dar"]
        self.level = 1
        super(Berserk, self).__init__(mudReaderHandler, telnetHandler)

class HealAbility(object):
    pass
    # @property 
    # def max_amount(self):
    #     raise NotImplementedError()

class Meditate(HealAbility, AbilityWithFailure):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "meditate"
        self.cooldown_after_success = 120
        self.cooldown_after_failure = 5
        self.max_amount = 26 #guess
        self.success_regex = "You feel at one with universe\."
        self.failure_regex = "Your spirit is not at peace\."
        # classes = ["Mon"]
        self.level = 4
        super(Meditate, self).__init__(mudReaderHandler, telnetHandler)

    def set_level(self, level):
        self.max_amount = 18 + level

class AestersTears(HealAbility, Ability):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "sing ae"
        self.cooldown_after_success = 140  # Can flee/move/attack immediately
        self.max_amount = 16  # guessed
        self.success_regex = "Your music rejuvenates everyone in the room\."  # This seems to overwrite Ability...
        # classes = ["Brd"]
        self.level = 4
        self.regexes = []
        super(AestersTears, self).__init__(mudReaderHandler, telnetHandler)

# danceOfTheCobra = FastCombatAbility(telnetHandler):
class DanceOfTheCobra(FastCombatAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "sing dance"  # needs target
        self.cooldown_after_success = 570  # can hit right away i believe
        self.cooldown_after_failure = 30  # can flee/move/attack
        # success_regex = r"The Dance of the Snake ends\.\n\rYou complete the ritual by touching the (.+?) and the charming takes effect\.\.\."
        self.success_regex = r"he Dance of the Snake ends"
        # failure_regex = r"The Dance of the Snake has no effect on the (.+?)\.\r\n"  # and you can hit right away.
        self.failure_regex = r"he Dance of the Snake has "
        # classes = ["Brd"]
        self.level = 1  # guessed
        # magentaprint("Dance of the Cobra regexes before calling super: " + str(self.regexes))
        self.regexes = []
        super(DanceOfTheCobra, self).__init__(mudReaderHandler, telnetHandler)
        # The mob just stops attacking, so how about turning off casting and just attacking him to death.
        # You can attack immediately after on success or fail.
        # But if you attacked then you have to wait to use it.

class Turn(FastCombatAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "turn"  # needs target
        self.cooldown_after_success = 30  # can attack immediately, but flee/move is 3 seconds later
        self.cooldown_after_failure = 30  # can attack immediately, but flee/move is 3 seconds later
                                     # (Said Please wait 1 sec THEN Please wait 2 sec)
        self.success_regex = "You turned the (.+?) for (.+?) damage\."  
        self.failure_regex = "You failed to turn the (.+?)\."
        # classes = ["Cle", "Pal"]
        self.level = 1

        # TODO: needs work:
        self.valid_targets = ["zombie", "skeleton", "ghast", "poltergeist", "geist", "ghoul"]
        super(Turn, self).__init__(mudReaderHandler, telnetHandler)

class Touch(CombatAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "touch"
        self.cooldown_after_success = 270
        self.cooldown_after_failure = 270
        self.success_regex = "You touched the (.+?) for (.+?) damage\."
        self.failure_regex = "You failed to harm the (.+?)\."
        # classes = ["Mon"]
        self.level = 4
        super(Touch, self).__init__(mudReaderHandler, telnetHandler)

class Wither(CombatAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "wither"
        self.cooldown_after_success = 300  # Guessed out of the blue
        self.cooldown_after_failure = 10  # can't attack/flee/move immediately
        self.success_regex = " the (.+?) for (.+?) damage\."  # Obviously needs work
        self.failure_regex = "Your withering touch did not hurt the (\.?)\."
        # classes = ["Dar"]
        self.level = 1
        super(Wither, self).__init__(mudReaderHandler, telnetHandler)

class Bash(CombatAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "bash"
        self.cooldown_after_success = 3
        self.cooldown_after_failure = 3
        self.success_regex = "You bash the (.+?), confusing them\."
        self.failure_regex = "You failed to bash it\."
        # classes = ["Bar", "Fig"]
        self.level = 1
        super(Bash, self).__init__(mudReaderHandler, telnetHandler)

class Circle(CombatAbility):
    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "circle"
        self.cooldown_after_success = 3
        self.cooldown_after_failure = 3
        self.success_regex = "You circle the (.+?)\."
        self.failure_regex = "You failed to circle it\."
        # classes = ["Bar", "Fig"]
        self.level = 1
        super(Circle, self).__init__(mudReaderHandler, telnetHandler)

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