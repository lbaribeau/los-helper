import time

from BotReactions import BotReactionWithFlag

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
    regexes = []
    timer = time.time()  # gives the time when the ability is available
    success = False  # check this value to see if use() was successful

    def __init__(self, telnetHandler):
        super(Ability, self).__init__()
        self.telnetHandler = telnetHandler
        self.regexes = self.regexes.append(self.success_regex)  # Hmmm
           # Needs to work when AbilityWithFlag calls it
           # and also when for instances of Ability.
        # super(Ability, self).__init__(self.regexes)

    @property
    def command(self): 
        raise NotImplementedError()
    @property
    def cooldown_after_success(self): 
        raise NotImplementedError()
    @property
    def success_regex(self):
        raise NotImplementedError()

    def notify(self, regex, M_obj):
        if regex is self.success_regex:
            self.success = True

        super(Ability, self).notify(regex, M_obj)

    def use(self, telnetHandler):
        if self.timer - time.time() < 0.75:
            time.sleep(self.timer - time.time())
        else:
            magentaprint("Ability: not ready for " + self.timer - time.time() + " seconds.")
            return

        self.success = False
        telnetHandler.write(self.command)
        self.timer = time.time() + self.cooldown_after_success

    def use_wait(self, telnetHandler):
        self.use(telnetHandler)
        self.wait_for_flag()

    def up(self):
        return self.timer < time.time()

    #def use_until_successful(self):
    # This will be done by AbilityThread
    # Maybe this can start a Ability thread

class AbilityWithFailure(Ability):
    # Some abilities never fail (sing aester,) but most do (buff abilities, meditate)
    @property
    def cooldown_after_failure(self): 
        raise NotImplementedError()
    @property
    def failure_regex(self):
        raise NotImplementedError()

    def __init__(self, telnetHandler):
        regexes = [self.failure_regex]
        super(AbilityWithFailure, self).__init__(telnetHandler)

    def notify(self, regex, M_obj):
        if regex is self.failure_regex:
            self.timer = self.timer - self.cooldown_after_success + self.cooldown_after_failure

        super(AbilityWithFailure, self).notify(regex, M_obj)


class BuffAbility(AbilityWithFailure):
    active = False

    @property 
    def already_buffed_regex(self):
        raise NotImplementedError()
    @property 
    def wear_off_regex(self):
        raise NotImplementedError() 

    def notify(self, regex, M_obj):
        if regex is self.success_regex:
            self.active = True
        elif regex is self.wear_off_regex:
            self.active = False

        super(BuffAbility, self).notify(regex, M_obj)


# Hint: the 'time' command in game tells you how much time is left on your buff
# Although I don't think I will use the 'lasts' variable.

# I could save a lot of data collection time by parsing the 
# 'time' output and filling in the cooldown info that way.

class Haste(BuffAbility):
    command = 'haste'
    cooldown_after_success = 600  # can flee
    cooldown_after_failure = 10  # can flee
    success_regex = 'You feel yourself moving faster\.'
    failure_regex = 'Your attempt to hasten failed\.'
    already_buffed_regex = "You're already hastened\."
    wear_off_regex = 'You feel slower\.'
    lasts = 150
    # classes = ["Ran"]
    level = 1

class Pray(BuffAbility):
    command = 'pray'
    cooldown_after_success = 610
    cooldown_after_failure = 10  # can flee
    success_regex = 'You feel extremely pious\.'
    failure_regex = 'Your prayers were not answered\.'
    already_buffed_regex = "You've already prayed\."
    wear_off_regex = 'You feel less pious\.'
    lasts = 310
    # classes = ["Cle", "Pal"]
    level = 1
    # I would do lasts 305 and cooldown 600 but I can't test that right now
   
class Barkskin(BuffAbility):
    command = 'barkskin' 
    cooldown_after_success = 600  # can flee, confirmed 10 minutes
    cooldown_after_failure = 10  # can flee
    success_regex = 'You feel your skin thickening and hardening\.'
    failure_regex = 'Your attempt to invoke barkskin failed\.'
    already_buffed_regex = "Your skin is already hardened\."
    wear_off_regex = 'Your skin softens\.'
    lasts = 120
    # classes = ["Dru"]
    level = 1

class Berserk(BuffAbility):
    command = 'berserk'
    cooldown_after_success = 600
    cooldown_after_failure = 20 
    success_regex = 'A red mist coats your vision, your heart pounds harder \. \. \.'
    failure_regex = 'You fail to work yourself into a frenzy\.'
    wear_off_regex = 'The red mist fades from your sight\.'  # Neato dark blue colored text
    lasts = 60
    # classes = ["Bar", "Dar"]
    level = 1

class HealAbility(object):
    @property 
    def max_amount(self):
        raise NotImplementedError()

class Meditate(HealAbility, AbilityWithFailure):
    command = 'meditate'
    cooldown_after_success = 120
    cooldown_after_failure = 5
    max_amount = 26 #guess
    success_regex = 'You feel at one with universe\.'
    failure_regex = 'Your spirit is not at peace\.'
    # classes = ["Mon"]
    level = 4

    def set_level(self, level):
        self.max_amount = 18 + level

class AestersTears(HealAbility, Ability):
    command = 'sing ae'
    cooldown_after_success = 140  # Can flee/move/attack immediately
    max_amount = 16  # guessed
    success_regex = 'Your music rejuvenates everyone in the room\.'
    # classes = ["Brd"]
    level = 4


class AbilityWithTarget(AbilityWithFailure):

    _command = NotImplementedError()

    def use(self, target):
        self.command = self._command + " " + target
        super(CombatAbility, self).use()
        self.cooldowns.ATTACK_CLK = time()

    def use_wait(self, target):
        self.use(target)
        self.wait_for_flag()


class FastCombatAbility(AbilityWithTarget):  
    # You can attack immediately after these abilities
    # FastTargetedAbility is another possible name
    pass

class CombatAbility(AbilityWithTarget):
    def use(self, target):
        super(CombatAbility, self).use()
        self.cooldowns.ATTACK_CLK = time()

class DanceOfTheCobra(FastCombatAbility):
    _command = 'sing dance'  # needs target
    cooldown_after_success = 570  # can hit right away i believe
    cooldown_after_failure = 30  # can flee/move/attack
    success_regex = "The Dance of the Snake ends\.\n\rYou complete the ritual by touching the (.+?) and the charming takes effect\.\.\."
    failure_regex = "The Dance of the Snake has no effect on the (.+?)\."  # and you can hit right away.
    # classes = ["Brd"]
    level = 1  # guessed
    # The mob just stops attacking, so how about turning off casting and just attacking him to death.
    # You can attack immediately after on success or fail.
    # But if you attacked then you have to wait to use it.

class Turn(FastCombatAbility):
    _command = 'turn'  # needs target
    cooldown_after_success = 30  # can attack immediately, but flee/move is 3 seconds later
    cooldown_after_failure = 30  # can attack immediately, but flee/move is 3 seconds later
                                 # (Said Please wait 1 sec THEN Please wait 2 sec)
    success_regex = "You turned the (.+?) for (.+?) damage\."  
    failure_regex = "You failed to turn the (.+?)\."
    # classes = ["Cle", "Pal"]
    level = 1

class Touch(CombatAbility):
    _command = 'touch'
    cooldown_after_success = 270
    cooldown_after_failure = 270
    success_regex = "You touched the (.+?) for (.+?) damage\."
    failure_regex = "You failed to harm the (.+?)\."
    # classes = ["Mon"]
    level = 4

class Wither(CombatAbility):
    _command = 'wither'
    cooldown_after_success = 300  # Guessed out of the blue
    cooldown_after_failure = 10  # can't attack/flee/move immediately
    success_regex = " the (.+?) for (.+?) damage\."  # Obviously needs work
    failure_regex = "Your withering touch did not hurt the (\.?)\."
    # classes = ["Dar"]
    level = 1

class Bash(CombatAbility):
    _command = 'bash'
    cooldown_after_success = 3
    cooldown_after_failure = 3
    success_regex = "You bash the (.+?), confusing them\."
    failure_regex = "You failed to bash it\."
    # classes = ["Bar", "Fig"]
    level = 1

class Circle(CombatAbility):
    _command = 'circle'
    cooldown_after_success = 3
    cooldown_after_failure = 3
    success_regex = "You circle the (.+?)\."
    failure_regex = "You failed to circle it\."
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