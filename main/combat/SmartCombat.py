
from threading import Thread

from combat.CombatObject import CombatObject
# from Ability import HealAbility, FastCombatAbility, CombatAbility, DanceOfTheCobra, Circle, Bash, Turn, Touch
from command.Ability import *
from misc_functions import magentaprint
from command import Spells
from comm import RegexStore
from combat.Kill import Kill
from combat.Cast import Cast
from reactions.Prompt import Prompt
from command.Use import Use

class SmartCombat(CombatObject):
    black_magic = True

    def __init__(self, telnetHandler, character):
        super().__init__(telnetHandler)
        self.thread = None
        self.target = None
        self.stopping = None
        self.kill = Kill(telnetHandler)
        self.cast = Cast(telnetHandler)
        self.prompt = Prompt(character)
        self.use = Use(character, telnetHandler)
        self.abilities = character._class.abilities.values()

        # self.heal_abilities = [a for a in self.abilities if isinstance(a, HealAbility)]
        # # self.heal_abilities_that_fail = [a for a in self.abilities if isinstance(a, HealAbility) and isinstance(a, AbilityWithFailure)]
        # self.fast_combat_abilities = [a for a in self.abilities if isinstance(a, FastCombatAbility)]
        # self.combat_abilities = [a for a in self.abilities if isinstance(a, CombatAbility)]
        self.heal_abilities = character._class.heal_skills
        self.buff_abilities = character._class.buff_skills
        self.combat_abilities = character._class.combat_skills
        self.fast_combat_abilities = character._class.fast_combat_skills

        spell_percent = max(character.earth, character.wind, character.fire, character.water)
        # magentaprint("SmartCombat character.pty " + str(character.pty))
        self.black_magic = character.pty < 7 or spell_percent >= 20
        # self.favourite_spell = Spells.vigor if not self.black_magic else \
        self.favourite_spell = Spells.rumble if spell_percent == character.earth else \
                               Spells.hurt if spell_percent == character.wind else \
                               Spells.burn if spell_percent == character.fire else Spells.blister
        # magentaprint("SmartCombat favourite_spell is \'" + self.favourite_spell + "\'.")  # works
        self.character = character
        self.regex_cart.append(RegexStore.prompt)

    def notify(self, regex, M_obj):
        # Notifications are used for healing
        # So SmartCombat needs to be registered/unregistered... or have a boolean for whether we're in combat.
        # I prefer the latter.
        super().notify(regex, M_obj)
        if regex in RegexStore.prompt:
            pass

    def stop(self):
        self.stopping = True

    def keep_going(self, target=None):
        self.stopping = False
        self.casting = True
        self.target = target if target else self.target

    def start_thread(self, target, spell=None):
        self.target = target
        self.spell = spell if spell else self.favourite_spell
        magentaprint("SmartCombat spell set to " + str(self.spell))

        # if self.thread is None or not self.thread.is_alive():
        if self.thread and self.thread.is_alive():
            self.keep_going(target)
        else:
            # not is_alive() means it won't look at stopping anymore so we're good.
            self.thread = Thread(target = self.run)
            self.thread.start()

    def run(self):
        self.stopping = False
        self.mob_charmed = False
        self.circled = False
        self.casting = self.black_magic or 'vigor' in self.character.spells

        self.use_any_fast_combat_abilities()  # ie. Touch

        while not self.stopping:
            # magentaprint("SmartCombat loop kill.timer " + str(round(self.kill.wait_time(), 1)) + " cast.timer " + str(round(self.cast.wait_time(), 1)) + ".")
            if self.kill.up() or self.kill.wait_time() <= self.cast.wait_time() or not self.casting:
                self.kill.wait_until_ready()
                if self.stopping: 
                    break 
                self.use_combat_ability_or_attack()
                # magentaprint("SmartCombat finished attack, stopping: " + str(self.stopping))
                # time.sleep(0.1)  
            else:
                self.cast.wait_until_ready()
                if self.stopping:
                    continue
                elif not self.black_magic and (self.character.MANA >= 2 and self.character.HEALTH <= self.character.maxHP - self.prompt.max_vigor()) or \
                     (self.character.MANA >= self.character.maxMP - 1 and self.character.HEALTH <= self.character.maxHP - self.prompt.max_vigor()/1.7):
                    # TODO: cast vigor if a tick is about to come and we're full mana
                    self.do_cast('v')
                elif self.mob_charmed:
                    time.sleep(min(0.2, self.kill.wait_time()))
                    # time.sleep(min(0.2, self.kill.wait_time() + 0.05))
                elif self.black_magic and ((self.spell in Spells.lvl1 and self.character.MANA >= 3) or 
                                           (self.spell in Spells.lvl2 and self.character.MANA >= 7)):  # Todo: add oom check
                    self.do_cast(self.spell, self.target) 
                elif self.black_magic and self.spell in Spells.lvl2 and self.character.MANA < 7 and self.character.MANA >= 3:
                    self.do_cast(Spells.lvl1[Spells.lvl2.index(self.spell)], self.target)
                else:
                    time.sleep(min(0.2, self.kill.wait_time()))

        magentaprint(str(self) + " ending run.")

    def do_cast(self, spell, target=None):
        self.cast.persistent_cast(spell, target)
        if self.cast.error:
            self.stop()

    def use_any_fast_combat_abilities(self):
        for a in self.fast_combat_abilities:
            # magentaprint("SmartCombat cycling abilities: " + str(a))
            if a.up():

                if isinstance(a, Turn):
                    if self.target not in a.valid_targets:
                        continue

                magentaprint("Using " + str(a))
                a.execute(self.target)
                a.wait_for_flag()
                magentaprint("SmartCombat finished using ability.")
                # So if we hit with Dance of the Cobra, we should save mana...
                if a.success and isinstance(a, DanceOfTheCobra):
                    self.mob_charmed = True
                elif a.error:
                    self.stop()
                # if self.stopping:
                #     return
                break

    def use_combat_ability_or_attack(self):
        for a in self.combat_abilities:
            if a.up():
                if isinstance(a, Bash):
                    continue  # For now, don't bash

                if isinstance(a, Circle):
                    if self.circled:
                        self.circled = False
                        continue
                    else:
                        self.circled = True
                
                magentaprint("SmartCombat executing " + str(a))
                a.execute(self.target)
                a.wait_for_flag()
                if a.error:
                    self.stop()
                return

        # self.attack_wait()
        self.kill.execute(self.target)
        self.kill.wait_for_flag()
        if self.kill.error:
            self.stop()
        # self.character.ATTACK_CLK = time.time()  # TODO: Kill should be smart enough to keep the clock set
                                                 # Kill should actually own the clock...

    @property
    def heal_ability_is_up(self):
        # self.heal_abilities[0].up()
        # return True if self.heal_abilities
        return any([a.up() for a in self.heal_abilities])

    # def flee(self):
    # I want to do the Go object first and get rid of MOVE_CLK

    def stop_casting(self):
        self.casting = False

