
import time, itertools

# from Command import Command
from command.ThreadingMixin2 import ThreadingMixin2
from combat.Kill import Kill
from reactions.BotReactions import BotReactionWithFlag
from comm import RegexStore
from misc_functions import magentaprint

# class Ability(ThreadingMixin2):
#     def __init__(self):
#         super().__init__()
#         self.end_thread_regexes = self.success_regexes + self.error_regexes

class Ability(ThreadingMixin2):
    def __init__(self, telnetHandler):   
        self.end_thread_regexes = self.success_regexes + self.error_regexes
        super().__init__(telnetHandler)
        # ThreadingMixin2.__init__(self, telnetHandler)
        # super().__init__(telnetHandler)

    # def notify(self, regex, M_obj):
    #     super().notify(regex, M_obj)
    #     if regex in itertools.chain.from_iterable(self.end_thread_regexes):
    #         magentaprint(str(self) + " ending thread.")
    #         self.stop()

    # @classmethod    
    # def run(cls, telnetHandler, target=None):
    #     # The result is only available on the object, not the class level.
    #     # Maybe that'll be fine.
    #     magentaprint("Sending '" + str(cls.command) + "' in " + str(round(cls.wait_time())) + "seconds.")
    #     cls.wait_until_ready()
    #     while not cls.stopping:
    #         cls.send(telnetHandler, target)
    #         cls.wait_for_class_flag()
    #         cls.wait_until_ready()

# class BuffAbility(AbilityWithFailure):
class BuffAbility(Ability):
    active = False

    # @property 
    # def already_buffed_regex(self):
    #     raise NotImplementedError()
    # @property 
    # def wear_off_regex(self):
    #     raise NotImplementedError() 

    def notify(self, regex, M_obj):
        if regex in self.success_regexes:
            self.active = True
        elif regex is self.wear_off_regex:
            # self.__class__.timer = time.time() + self.__class__.cooldown_after_success - self.lasts
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

class CombatAbility(Ability):
    pass
    # error_regexes = [RegexStore.not_here]
    # def notify(self, r, m):
    #     if r in RegexStore.not_here and not self._waiter_flag:
    #         # Ability was getting incorrectly reset on 'They are not here'
    #         self.clear_timer()
    #     super().notify(r, m)

class FastCombatAbility(CombatAbility):  
    # You can attack immediately after these abilities
    # FastTargetedAbility is another possible name
    pass  # We're just using this for a kind of 'typing' for the smartCombat logic

class SlowCombatAbility(CombatAbility):
    # Bash, Circle, Touch, Wither

    # def notify(self, r, m):
    #     if r in regexstore.not_here and not self._waiter_flag:
    #         kill.clear_timer()  
    #         # error case if combatability.execute() is called when not up() this can incorrectly shorten kill's cooldown
    #         # solution would be to wait for notificiations to adjust the kill timer but that has drawbacks too
    #         #  (timer in limbo for brief period until server responds)
    #     super().notify(r, m)

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
    command = "has"
    cooldown_after_success = 600  # can flee
    cooldown_after_failure = 10  # can flee
    # success_regexes = [r"You feel yourself moving faster\."]
    success_regexes = [RegexStore.hastened, RegexStore.already_hastened]
    failure_regexes = [RegexStore.haste_fail]
    already_buffed_regex = RegexStore.already_hastened
    # wear_off_regex = "You feel slower\."
    wear_off_regex = RegexStore.feel_slower
    lasts = 150
    # self.classes = ["Ran"]
    level = 1

class Pray(BuffAbility):
    command = "pra"
    cooldown_after_success = 604
    cooldown_after_failure = 10  # can flee
    success_regexes = [RegexStore.prayers_answered, RegexStore.already_prayed] # [r"You feel extremely pious\."]
    failure_regexes = [RegexStore.not_answered] # [r"Your prayers were not answered\."]
    already_buffed_regex = RegexStore.already_prayed
    wear_off_regex = RegexStore.feel_less_pious #"You feel less pious\."
    lasts = 310
    # self.classes = ["Cle", "Pal"]
    level = 1
        # I would do lasts 305 and cooldown 600 but I can't test that right now
   
class Barkskin(BuffAbility):
    command = "bar" 
    cooldown_after_success = 600  # can flee, confirmed 10 minutes
    cooldown_after_failure = 10  # can flee
    success_regexes = [RegexStore.skin_thickening, RegexStore.already_hardened]
    failure_regexes = [RegexStore.barkskin_failed]
    already_buffed_regex = RegexStore.already_hardened
    wear_off_regex = RegexStore.skin_softens
    lasts = 120
    # classes = ["Dru"]
    level = 1

class Berserk(BuffAbility):
    command = "ber"
    cooldown_after_success = 600
    cooldown_after_failure = 20 
    success_regexes = [RegexStore.red_mist, RegexStore.already_berserk]
    failure_regexes = [RegexStore.berserk_fail]
    already_buffed_regex = RegexStore.already_berserk
    wear_off_regex =  RegexStore.red_mist_fades
    lasts = 60
    # classes = ["Bar", "Dar"]
    level = 1

class HealAbility(Ability):
    def set_level(self, level):
        self.__class__.max_amount = 16 + int(round(1.4*level, 0))
    # @property 
    # def max_amount(self):
    #     raise NotImplementedError()

class Search(Ability):
    command = 'sea'
    cooldown_after_success = 8
    cooldown_after_failure = 8
    success_regexes = [RegexStore.found_exit]
    failure_regexes = [RegexStore.search_fail]
    level = 1

class Prepare(Ability):
    command = 'prep'
    cooldown_after_success = 8
    cooldown_after_failure = 8
    success_regexes = [RegexStore.prepare, RegexStore.already_prepared]
    failure_regexes = []
    level = 1

class Hide(Ability):
    command = 'hid'
    cooldown_after_success = 11
    cooldown_after_failure = 11
    success_regexes = [RegexStore.hide]
    failure_regexes = [RegexStore.hide_fail]
    level = 1

class Meditate(HealAbility):
    command = "me"
    cooldown_after_success = 120
    cooldown_after_failure = 5
    max_amount = 15 #guess  ()
    success_regexes = [RegexStore.meditate]
    failure_regexes = [RegexStore.not_at_peace]
    # classes = ["Mon"]
    level = 4

class AestersTears(HealAbility):
    command = "sin a"
    cooldown_after_success = 140  # Can flee/move/attack immediately
    max_amount = 16  # guessed
    success_regexes = [RegexStore.aesters_tears]  # This seems to overwrite Ability...
    # self.failure_regex = "(?!x)x"  # Regex that never matches - Aester never fails
    failure_regexes = []
    # classes = ["Brd"]
    level = 4

# danceOfTheCobra = FastCombatAbility(telnetHandler):
class DanceOfTheCobra(FastCombatAbility):
    command = "sin d"  # needs target
    cooldown_after_success = 570  # can hit right away i believe
    cooldown_after_failure = 30  # can flee/move/attack
    # success_regex = r"The Dance of the Snake ends\.\n\rYou complete the ritual by touching the (.+?) and the charming takes effect\.\.\."
    # success_regexes = [r"he Dance of the Snake ends"]
    success_regexes = [RegexStore.dance_of_the_cobra]
    # failure_regex = r"The Dance of the Snake has no effect on the (.+?)\.\r\n"  # and you can hit right away.
    failure_regexes = [RegexStore.dance_of_the_cobra_fail]
    error_regexes = [RegexStore.dance_whom, RegexStore.not_here]
    # classes = ["Brd"]
    level = 1  # guessed
    # magentaprint("Dance of the Cobra regexes before calling super: " + str(self.regexes))
    # The mob just stops attacking, so how about turning off casting and just attacking him to death.
    # You can attack immediately after on success or fail.
    # But if you attacked then you have to wait to use it.

class Turn(FastCombatAbility):
    command = "tu"  # needs target
    cooldown_after_success = 30  # can attack immediately, but flee/move is 3 seconds later
    cooldown_after_failure = 30  # can attack immediately, but flee/move is 3 seconds later
                                 # (Said Please wait 1 sec THEN Please wait 2 sec)
    success_regexes = [RegexStore.turn]
    failure_regexes = [RegexStore.turn_fail, RegexStore.turn_living_target]
    error_regexes = [RegexStore.turn_whom, RegexStore.not_here]
    # classes = ["Cle", "Pal"]
    level = 1

    # TODO: needs work:
    valid_targets = ['zombie', 'skeleton', 'ghast', 'poltergeist', 'geist', 'ghoul', 'shadow lich', 
        'shadowed huorn']

class Touch(SlowCombatAbility):
    command = "to"
    cooldown_after_success = 270
    cooldown_after_failure = 270
    success_regexes = [RegexStore.touch]
    failure_regexes = [RegexStore.touch_fail]
    error_regexes = [RegexStore.touch_whom, RegexStore.not_here]
    # classes = ["Mon"]
    level = 10

    # def notify(self, r, m):
    #     magentaprint('Touch notified, timer: ' + str(round(self.__class__.timer - time.time(), 0)))
    #     super().notify(r, m)
    #     magentaprint('Touch notified 2, timer: ' + str(round(self.__class__.timer - time.time())))

class Wither(SlowCombatAbility):
    command = "withe"
    cooldown_after_success = 240  # Guessed out of the blue
    cooldown_after_failure = 10  # can't attack/flee/move immediately
    success_regexes = [RegexStore.wither]  # regex needs work
    failure_regexes = [RegexStore.wither_fail]
    error_regexes = [RegexStore.wither_whom, RegexStore.not_here]
    # classes = ["Dar"]
    level = 1

class Bash(SlowCombatAbility):
    command = "bas"
    cooldown_after_success = 3
    cooldown_after_failure = 3
    success_regexes = [RegexStore.bash]
    failure_regexes = [RegexStore.bash_fail]
    error_regexes = [RegexStore.bash_whom, RegexStore.not_here]
    # classes = ["Bar", "Fig"]
    level = 1

class Circle(SlowCombatAbility):
    command = "ci"
    cooldown_after_success = 3
    cooldown_after_failure = 3  # 4 I think
    success_regexes = [RegexStore.circle]
    failure_regexes = [RegexStore.circle_fail]
    error_regexes = [RegexStore.circle_whom, RegexStore.not_here]
    # classes = ["Bar", "Fig"]
    level = 1

    def notify(self, r, m):
        super().notify(r, m)
        if r in RegexStore.circle_fail:
            Kill.timer = Kill.timer + 1

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
