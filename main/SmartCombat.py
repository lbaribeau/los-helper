import CombatThread
from Abilities import *
from misc_functions import *

class SmartCombat(CombatThread, BotReactionWithFlag):
	''' This thread is an alternative to the simpler KillThread and CastThread.
    It will fight smart.  It will use all of your abilities and spells in a 
    smart order until your enemy dies.  It will also use restoratives.  It will 
    even flee.  It won't choose your spell for you though.  '''

    healing = False
    # cast_up = True
    attack_flag = False
    cast_flag = False

    def __init__(self, character, mudReaderHandler, telnetHandler, target, 
                 inventory, abilities, spell=None):
        super(SmartCombat, self).__init__(character, mudReaderHandler, 
                                          telnetHandler, target)
        self.inventory = inventory
        self.heal_abilities = filter(isinstance(HealAbility), abilities)
        self.heal_abilities_that_fail = filter(isinstance(AbilityWithFailure), 
                                               self.heal_abilities)
        self.fast_combat_abilities = filter(isinstance(FastCombatAbility), abilities)
        self.combat_abilities = filter(isinstance(CombatAbility), abilities)

        self.health_mana = "\[(\d+?) H (\d+?) M\]"
        self.potion_drank = ["Potion drank\."]
        self.kill_return = []
        self.cast_return = []
        self.vig_return = []
        self.bad_target = ["You don't see that here\.",
                           "Attack what\?,"
                           # Need more from the Abilities
                           ]
        self.spell_fail = []

        self.regexes.extend([a.success_regex for a in abilities])
        self.regexes.extend([a.failure_regex for a in self.heal_abilities_that_fail])
        self.regexes.extend([a.failure_regex for a in self.fast_combat_abilities])
        self.regexes.extend([a.failure_regex for a in self.combat_abilities])
        self.regexes.extend([
                             self.potion_drank,
                             self.kill_return,
                             self.bad_target,
                             self.spell_fail,
                             self.health_mana,

        self.spell = spell if spell is not None else self.character.FAVOURITE_SPELL
        self.max_vig = round(self.character.piety / 3)  #guess

    def notify(self, regex, M_obj):
        if regex is self.health_mana:
            self.react_to_health(M_obj.group(1))
        elif regex in [a.success_regex for a in self.heal_abilities] or \
             regex in [a.failure_regex for a in self.heal_abilities_that_fail] or \
             regex is self.potion_drank or \
             regex is self.vig_return:
            self.healing = False  # Hopefully pots get appropriately spammed... test with high flee health
                                  # I put health_mana last to help healing = False to happen first
        elif regex in self.kill_return:
            self.attack_flag = True
        elif regex in self.cast_return:
            self.cast_flag = True
        elif regex is self.spell_fail:
            if not self.character.BLACK_MAGIC:
                self.cast()
        else:
        # elif regex is self.it_collapsed or self.it_fled:  # TODO: party kill regex
            self.stop()

        self.__waiter_flag = True

    def react_to_health(self, hp):
        if self.healing:
            return

        for heal_ability in self.heal_abilities:
            if hp < self.character.MAXHP - heal_ability.max_amount and heal_ability.up():
                self.healing = True
                heal_ability.use()
                return

        if not self.BLACK_MAGIC and self.cast_up and self.character.MAXHP - hp > self.max_vigor:
            self.cast()
            # Let's not count vigor on self.healing because that is for behavior near HEALTH_TO_FLEE

        if hp < self.character.HEALTH_TO_FLEE:
            if self.inventory.has_restorative():
                self.healing = True
                self.inventory.use_restorative()
            else:
                self.flee()

    def run(self):
        self.stopping = False
        self.mudReaderHandler.register_reaction(self)
        self.circled = False
        wait_for_attack_ready(self.character)

        if self.character.BLACK_MAGIC:
            wait_for_cast_ready()

        # if fast_combat_abilities:
        #     fast_ability_timer = min([a.timer for a in self.fast_combat_abilities])
        # else:
        #     fast_ability_timer = 1000

        for a in self.fast_combat_abilities:
            if a.up():
                a.use_wait()
                if self.stopping:
                    return
                break

        while not self.stopping:
            if attack_wait() <= cast_wait():
                wait_for_attack_ready()
                break if self.stopping
                self.use_combat_ability_or_attack()
                # time.sleep(0.1)  
            else:
                wait_for_cast_ready()
                break if self.stopping
                if self.character.BLACK_MAGIC:
                    self.cast()
                elif self.character.HEALTH <= self.character.MAXHP - self.max_vigor:
                    self.cast()
                    # time.sleep(0.1)
                else:
                    wait_for_attack_ready()

    def use_combat_ability_or_attack(self):
        for a in self.combat_abilites:
            if a.up():
                if isinstance(a, Bash):
                    continue

                if isinstance(a, Circle):
                    if self.circled:
                        self.circled = False
                        continue
                    else:
                        self.circled = True

                a.use_wait()
                return

        self.attack()

    def attack_wait(self):
        self.attack_flag = False
        self.attack()
        busy_loop(self.attack_flag)

    def attack(self):
        self.character.ATTACK_CLK = time()
        self.telnetHandler.write("k " + target)

    def cast_wait(self):
        self.cast_flag = False
        self.cast()
        busy_loop(self.cast_flag)

    def cast(self):
        self.character.CAST_CLK = time()
        if self.character.BLACK_MAGIC:
            self.telnetHandler.write("c " + self.character.FAVOURITE_SPELL + " " + self.target)
        else:
            self.telnetHandler("c vig")






        # How about I just define a rotation... it'll probably work
        # Don't vig at the start in case it's a level 1 - vig at the 
        # same time you'd case black magic.  Well, what if we just 
        # exited heal up... it'd be nice not to be too rigid.
        # Maybe at the end of every loop we wait for the next thing to be up.
        # The only interruption is if the mob dies.  BotThread can move on 
        # while we finish our sleep.

        # So, how about we determine our next attack.  Prioritize damage... 
        # then trust notify to react.  Holy cow this is difficult.












        if not self.character.BLACK_MAGIC:
            self.
        self.act()

    def act(self):

    def vigor_up(self):

    # def cast_up(self):
    #     return time() > cast_timer
    #     Better keep track of this myself so I'm not calling time() a gazillion times

        if any(d.up() for d in self.damage_abilities):





        


# RUN

        # Use damage ability, on return fail use kill, else 3 sec later use kill
        # Wait for kill to register and hit cast and register another cast 
        # 3 sec later (unless cast fail)
        # We could may as well make use of cast thread here...
        # I would just be worried about casting at the same time as attacking,
        # but I think that would be pretty well avoided... well maybe not, 
        # it might hit cast milliseconds before stop is called (when you find 
        # out a mob died from kill.)  So better do casting here.  Queue up each 
        # cast when kill returns.


# Should this flee?  Yes.  Then botThread will have nothing to worry 
# about.  It is a new thread so fleeing is superior, because the human/bot 
# will always have control to stop it and flee if they so desire.  

# It'd be nice to inherit from CombatThread.  Multiple inheritance will be 
# too hard though!  Ack!  I don't know what I'm doing!!!  (too hard because 
# parentA and parentB take different arguments to init!)

# I think that the clock variables should remain global.  They're in character, 
# but even an all-encompassing class like this doesn't seem to deserve to own 
# them.  

# It'd be nice if BotReactions didn't need mudReaderHandler.

                 # MULTIPLE INHERITANCE
                 # regexes same as CombatThread...
                 # Oooofff I could do this the same way as kill thread.
                 # I believe ThreadStoppers get around this...
                 # I could delete __init__ from BotReaction.
                 # Multiple inheritance needs orthogonal features.
                 # Ok I got it.  I have no need for BotReaction.  
                 # I will just not inherit it.
                 # Well, I could make use of BotReactionWithFlag.  
                 # So even better, I will just delete BotReaction as it is 
                 # unneeded.  Because Python!!!!!  Yes Python is awesome 
                 # and I believe this is a great way to do.


# idea: each ability should have a class/level criteria static method.  Then 
# we can read character to assemble the abilities, possible in SmartCombat, 
# or possibly somewhere like commandHandler

# TYPING
# heal abilites, damage abilities, combat abilities.  Apparently type checking 
# isn't pythonic, "duck typing" is preferred, where you try to do what you would 
# do, and catch the exception if it doesn't work.  I think that is more for 
# lists and strings.  I think what I'm doing is okay.  

# You use your .+ to strike the .+ for \d damage\.