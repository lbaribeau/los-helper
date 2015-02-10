
from itertools import chain

from CombatThread import CombatThread
from Ability import *
import misc_functions
from Command import Kill

# class SmartCombat(BotReactionWithFlag, CombatThread):
class SmartCombat(CombatThread, BotReactionWithFlag):
    ''' This thread is an alternative to the simpler KillThread and CastThread.
    It will fight smart.  It will use all of your abilities and spells in a 
    smart order until your enemy dies.  It will also use restoratives.  It will 
    even flee.  It won't choose your spell for you though.  '''

    healing = False
    # cast_up = True
    attack_flag = False
    cast_flag = False

    # kill_return is at the bottom because it's huge
    cast_return = "You cast a \S+ spell on .+?\.\n\r"
            # "The spell did \d+ damage\."]
    spell_fail = "Your spell fails\."

    health_mana = "\[(\d+?) H (\d+?) M\]"
    potion_drank = "Potion drank\."
    
    vig_return = "Vigor spell cast\."
    bad_target = ["You don't see that here\.",
                  "Attack what\?"
                  # Need more from the Abilities
    ]

    def __init__(self, character, mudReaderHandler, telnetHandler, target, 
                 inventory, spell=None):
        super(SmartCombat, self).__init__(character, mudReaderHandler, 
                                          telnetHandler, target)
        self.inventory = inventory
        # self.heal_abilities = filter(isinstance(HealAbility), self.character._class.abilities)
        # self.heal_abilities_that_fail = filter(isinstance(AbilityWithFailure), 
        #                                        self.heal_abilities)
        # self.fast_combat_abilities = filter(isinstance(FastCombatAbility), self.character._class.abilities)
        # self.combat_abilities = filter(isinstance(CombatAbility), self.character._class.abilities)
        self.heal_abilities = [a for a in self.character._class.abilities if isinstance(a, HealAbility)]
        self.heal_abilities_that_fail = [a for a in self.character._class.abilities if isinstance(a, HealAbility) and isinstance(a, AbilityWithFailure)]
        self.fast_combat_abilities = [a for a in self.character._class.abilities if isinstance(a, FastCombatAbility)]
        self.combat_abilities = [a for a in self.character._class.abilities if isinstance(a, CombatAbility)]

        # self.regexes.extend([a.success_regex for a in self.character._class.abilities])
        # self.regexes.extend([a.failure_regex for a in self.heal_abilities_that_fail])
        # self.regexes.extend([a.failure_regex for a in self.fast_combat_abilities])
        # self.regexes.extend([a.failure_regex for a in self.combat_abilities])

        # [item for sublist in l for item in sublist]
        # self.regexes.extend([].extend(
        #     self.cast_return,
        #     self.kill_return,
        #     self.bad_target,
        #     self.spell_fail,
        #     self.potion_drank,
        #     self.health_mana
        # ])
        self.regexes.extend([
            self.cast_return,
            self.spell_fail,
            self.potion_drank,
            self.health_mana
        ])
        self.regexes.extend(self.kill_return)
        self.regexes.extend(self.bad_target)
        magentaprint(self.regexes)
        self.spell = spell if spell is not None else self.character.FAVOURITE_SPELL
        self.max_vig = round(self.character.pty / 2)  #guess

    def notify(self, regex, M_obj):
        if regex in self.bad_target:
            self.attack_flag = True
            self.stop()
        elif regex is self.health_mana:
            self.react_to_health(int(M_obj.group(1)))
        elif regex in [a.success_regex for a in self.heal_abilities] or \
             regex in [a.failure_regex for a in self.heal_abilities_that_fail] or \
             regex is self.potion_drank or \
             regex is self.vig_return:
            self.healing = False  # Hopefully pots get appropriately spammed... test with high flee health
                                  # I put health_mana last to help healing = False to happen first
        elif regex in self.kill_return:
            magentaprint("SmartCombat notify kill_return")
            self.attack_flag = True
        elif regex is self.cast_return or regex is self.vig_return:
            self.cast_flag = True
        elif regex is self.spell_fail:
            if not self.character.BLACK_MAGIC:
                self.cast()
            else:
                self.cast_flag = True
        else:
            # elif regex is self.it_collapsed or self.it_fled:  # TODO: party kill regex
            magentaprint("SmartCombat notified on regex " + regex + ", stopping")
            # magentaprint("SmartCombat regexes: " + str(self.regexes))
            if regex is self.health_mana:
                magentaprint("Crazy")
            else:
                magentaprint("Not")
            self.stop()

        self._waiter_flag = True

    def react_to_health(self, hp):
        if self.healing:
            return

        for heal_ability in self.heal_abilities:
            if hp < self.character.maxHP - heal_ability.max_amount and heal_ability.up():
                self.healing = True
                heal_ability.use()
                return

        if not self.character.BLACK_MAGIC and misc_functions.cast_ready() and self.character.maxHP - hp > self.max_vigor:
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
        misc_functions.wait_for_attack_ready(self.character)

        if self.character.BLACK_MAGIC:
            misc_functions.wait_for_cast_ready(self.character)

        # if fast_combat_abilities:
        #     fast_ability_timer = min([a.timer for a in self.fast_combat_abilities])
        # else:
        #     fast_ability_timer = 1000

        for a in self.fast_combat_abilities:
            magentaprint("Cycling abilities: " + str(a))
            if a.up():
                magentaprint("Using " + str(a))
                a.use_wait(self.target)
                magentaprint("SmartCombat finished using ability.")
                # if self.stopping:
                #     return
                break

        while not self.stopping:
            magentaprint("SmartCombat loop")
            if misc_functions.attack_wait(self.character) <= misc_functions.cast_wait(self.character):
                misc_functions.wait_for_attack_ready(self.character)
                magentaprint("SmartCombat attack is ready")
                if self.stopping: 
                    break 
                self.use_combat_ability_or_attack()
                magentaprint("SmartCombat finished attack, stopping: " + str(self.stopping))
                # time.sleep(0.1)  
            else:
                misc_functions.wait_for_cast_ready(self.character)
                magentaprint("SmartCombat cast is ready.")
                if self.stopping:
                    break
                if self.character.BLACK_MAGIC:
                    self.cast_wait()
                elif self.character.HEALTH <= self.character.maxHP - self.max_vigor:
                    self.cast()
                    # time.sleep(0.1)
                else:
                    misc_functions.wait_for_attack_ready(self.character)

        magentaprint("SmartCombat exiting run()")

    def use_combat_ability_or_attack(self):
        for a in self.combat_abilities:
            if a.up():
                if isinstance(a, Bash):
                    continue

                if isinstance(a, Circle):
                    if self.circled:
                        self.circled = False
                        continue
                    else:
                        self.circled = True

                if isinstance(a, Turn):
                    if self.target not in a.valid_targets:
                        continue

                a.use_wait(self.target)
                self.character.ATTACK_CLK = time.time()
                return

        # magentaprint("SmartCombat calling attack_wait")
        # self.attack_wait()
        magentaprint("SmartCombat calling Kill")
        Kill(self.mudReaderHandler, self.telnetHandler).execute_and_block(self.target)


    def attack_wait(self):
        self.attack_flag = False
        self.attack()
        magentaprint("SmartCombat beginning busy loop.")
        # misc_functions.busy_loop(self.attack_flag)
        while not self.attack_flag:
            time.sleep(0.02)
        magentaprint("SmartCombat attack wait finished.")

    def attack(self):
        self.character.ATTACK_CLK = time.time()
        self.telnetHandler.write("k " + self.target)

    def cast_wait(self):
        self.cast_flag = False
        self.cast()
        # misc_functions.busy_loop(self.cast_flag)
        while not self.cast_flag:
            time.sleep(0.02)
        magentaprint("SmartCombat cast wait finished.")

    def cast(self):
        self.character.CAST_CLK = time.time()
        if self.character.BLACK_MAGIC:
            self.telnetHandler.write("c " + self.character.FAVOURITE_SPELL + " " + self.target)
        else:
            self.telnetHandler("c vig")

    kill_return = [
        # "You attack the (.+?)\."  # Beginning combat
        # r"You swing with your .+?, hacking the (.+?) for \d+ damage\.",
        # r"You hack with your .+?, but your blow swings wide of the mark\.",
        # r"You slice the (.+?) for \d+ damage with your .+?\.",
        # r"You slice your (.+?) at the .+?, but miss\.",
        # r"You slash at the (.+?) and hit for \d+ damage\.",
        # r"You slash at the (.+?), but miss\.",

        # r"You chop at the (.+?) for \d+ damage\.",
        # r"You chop at the (.+?) but fail to hit them\.",
        # r"You stab at the (.+?) with your .+?, causing \d+ damage"
        # r"You try to stab the (.+?) with your .+?, but miss\.",
        # r"You lunge at the (.+?), striking for \d+ damage\.",
        # r"You lunge wildly at the (.?+) but mistime the strike\.",

        # r"You lash out and thump the (.+?) for \d+ damage\.",
        # r"You lash out at the (.+?), but miss\.",
        # r"You punch the (.+?) for \d+ damage\.",
        # r"You swing a wild punch at the (.+?), but it misses\.",
        # r"You kick the (.+?) for \d+ damage\."
        # r"You kick at the (.+?), but fail to hurt them\.",
        # r"You head-butt the (.+?) for \d+ damage\."
        # r"You grab at the (.+?), but (s?he|it) escapes your grasp\.",
        # r"You grab the (.+?) and gouge (him|her|it) for \d+ damage\.",
        # r"You try to gouge the (.+?), but can't get a good grip\.",

        # r"You smash your .+? into the (.+?), causing \d+ damage\.",
        # r"You swing your .+? at the (.+?), but miss\.",
        # r"You heave your .+? at the (.+?), smashing (him|her|it) for \d+ damage\.",
        # r"You heave your .+? in a wide arc, but fail to hit anything\.",
        # r"You bludgeon the (.+?) for \d+ damage\.",
        # r"You try to bludgeon the (.+?), but miss\.",

        # r"You lunge at the (.+?), hitting them for \d+ damage\.",
        # r"You lunge at the (.+?), but you miss\.",
        # r"You swing your .+?, striking for \d+ damage\.",
        # r"Your .+? swings, but fails to connect\.",
        # r"You sweep the (.+?) with your .+? for \d+ damage\.",
        # r"You sweep at the (.+?) with your .+?, but miss\.",

        r"Your missile slams into the (.+?) for \d+ damage\.",
        r"Your missile arcs towards the (.+?), but fails to hit them\.",
        r"You attack the (.+?) with your .+?, striking for \d+ damage\.",
        r"You attack the (.+?) with your .+?, but miss\.",
        r"You use your .+? to strike the (.+?) for \d+ damage\.",
        r"You use your .+?, but nothing hits the (.+?)\."
    ]



        # How about I just define a rotation... it'll probably work
        # Don't vig at the start in case it's a level 1 - vig at the 
        # same time you'd case black magic.  Well, what if we just 
        # exited heal up... it'd be nice not to be too rigid.
        # Maybe at the end of every loop we wait for the next thing to be up.
        # The only interruption is if the mob dies.  BotThread can move on 
        # while we finish our sleep.

        # So, how about we determine our next attack.  Prioritize damage... 
        # then trust notify to react.  Holy cow this is difficult.












    #     if not self.character.BLACK_MAGIC:
    #         self.
    #     self.act()

    # def act(self):

    # def vigor_up(self):

    # # def cast_up(self):
    # #     return time() > cast_timer
    # #     Better keep track of this myself so I'm not calling time() a gazillion times

    #     if any(d.up() for d in self.damage_abilities):





        


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
# heal abilities, damage abilities, combat abilities.  Apparently type checking 
# isn't pythonic, "duck typing" is preferred, where you try to do what you would 
# do, and catch the exception if it doesn't work.  I think that is more for 
# lists and strings.  I think what I'm doing is okay.  

# You use your .+ to strike the .+ for \d damage\.