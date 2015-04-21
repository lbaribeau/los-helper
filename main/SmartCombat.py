
from threading import Thread

from CombatObject import CombatObject
from Ability import HealAbility, FastCombatAbility, CombatAbility, DanceOfTheCobra
from misc_functions import magentaprint

class SmartCombat(CombatObject):
    black_magic = True

    def __init__(self, telnetHandler, kill, cast, character):
        super().__init__(telnetHandler)
        self.thread = None
        self.target = None
        self.stopping = None
        self.kill = kill
        self.cast = cast
        self.abilities = character._class.abilities
        self._class = character._class

        self.heal_abilities = [a for a in self.abilities if isinstance(a, HealAbility)]
        # self.heal_abilities_that_fail = [a for a in self.abilities if isinstance(a, HealAbility) and isinstance(a, AbilityWithFailure)]
        self.fast_combat_abilities = [a for a in self.abilities if isinstance(a, FastCombatAbility)]
        self.combat_abilities = [a for a in self.abilities if isinstance(a, CombatAbility)]

        spell_percent = max(character.earth, character.wind, character.fire, character.water)
        self.black_magic = character.pty < 7 or spell_percent >= 20
        self.favourite_spell = 'rum' if spell_percent == character.earth else \
                               'hurt' if spell_percent == character.wind else \
                               'burn' if spell_percent == character.fire else 'blis'
        # magentaprint("SmartCombat favourite_spell is \'" + self.favourite_spell + "\'.")  # works


    def notify(self, regex, M_obj):
        # Notifications are used for healing
        # So SmartCombat needs to be registered/unregistered... or have a boolean for whether we're in combat.
        # I prefer the latter.
        super().notify(regex, M_obj)

    def stop(self):
        self.stopping = True

    def keep_going(self, target=None):
        self.stopping = False
        self.target = target if target else self.target

    def start_thread(self, target):
        # magentaprint("SmartCombat: engage" + str(self))
        # magentaprint("telnetHandler: " + str(self.telnetHandler))

        self.target = target

        if self.thread is None or not self.thread.is_alive():
            # not is_alive() means it won't look at stopping anymore so we're good.
            self.thread = Thread(target = self.run)
            self.thread.start()

    def run(self):
        # This function defines combat, and it works for ALL classes.
        self.stopping = False
        self.mob_charmed = False
        self.casting = True

        self.use_any_fast_combat_abilities()  # ie. Touch

        while not self.stopping:

            if self.kill.timer <= self.cast.timer or self.kill.up() or not self.casting:
                self.kill.wait_until_ready()
                if self.stopping: 
                    break 
                self.use_combat_ability_or_attack()
                # magentaprint("SmartCombat finished attack, stopping: " + str(self.stopping))
                # time.sleep(0.1)  
            else:
                self.cast.wait_until_ready()
                if self.stopping or self.mob_charmed:
                    continue
                if self.black_magic:
                    self.cast.__class__.command = 'cas ' + self.favourite_spell
                    self.cast.execute(self.target)  # use cast.cast maybe
                elif self.character.HEALTH <= self.character.maxHP - self.max_vigor:
                    self.cast.__class__.command = 'cas vi'
                    self.cast.execute()
                else:
                    self.kill.wait_until_ready()

        magentaprint(str(self) + " ending run.")

    def use_any_fast_combat_abilities(self):
        for a in self.fast_combat_abilities:
            # magentaprint("SmartCombat cycling abilities: " + str(a))
            if a.up():
                magentaprint("Using " + str(a))
                a.execute(self.target)
                a.wait_for_flag()
                magentaprint("SmartCombat finished using ability.")
                # So if we hit with Dance of the Cobra, we should save mana...
                if a.result is 'success' and isinstance(a, DanceOfTheCobra):
                    self.mob_charmed = True
                elif a.result is 'error':
                    self.stopping = True
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

                if isinstance(a, Turn):
                    if self.target not in a.valid_targets:
                        continue

                a.execute(self.target)
                a.wait_for_flag()
                return

        # self.attack_wait()
        self.kill.execute(self.target)
        self.kill.wait_for_flag()
        if self.kill.result is 'error':
            self.stopping = True
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

