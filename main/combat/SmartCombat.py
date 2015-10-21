
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
from command.Wield import Wield

class SmartCombat(CombatObject):
    black_magic = True

    def __init__(self, telnetHandler, character):
        super().__init__(telnetHandler)
        self.thread = None
        self.target = None
        self.stopping = None
        self.broken_weapon = ''
        self.kill = Kill(telnetHandler)
        self.cast = Cast(telnetHandler)
        self.prompt = Prompt(character)
        self.use = Use(character, telnetHandler)
        self.wield = Wield(character, telnetHandler)
        self.abilities = character._class.abilities.values()

        # self.heal_abilities = [a for a in self.abilities if isinstance(a, HealAbility)]
        # # self.heal_abilities_that_fail = [a for a in self.abilities if isinstance(a, HealAbility) and isinstance(a, AbilityWithFailure)]
        # self.fast_combat_abilities = [a for a in self.abilities if isinstance(a, FastCombatAbility)]
        # self.combat_abilities = [a for a in self.abilities if isinstance(a, CombatAbility)]
        self.heal_abilities = character._class.heal_skills
        self.buff_abilities = character._class.buff_skills
        self.slow_combat_abilities = character._class.slow_combat_skills
        self.fast_combat_abilities = character._class.fast_combat_skills

        spell_percent = max(character.earth, character.wind, character.fire, character.water)
        # magentaprint("SmartCombat character.pty " + str(character.pty))
        self.black_magic = character.pty < 7 or spell_percent >= 5
        # self.favourite_spell = Spells.vigor if not self.black_magic else \
        if spell_percent == 0 and self.black_magic:
            self.favourite_spell = Spells.rumble if Spells.rumble in character.spells else \
                                   Spells.hurt if Spells.hurt in character.spells else \
                                   Spells.burn if Spells.burn in character.spells else Spells.blister
        else:
            self.favourite_spell = Spells.rumble if spell_percent == character.earth else \
                                   Spells.hurt if spell_percent == character.wind else \
                                   Spells.burn if spell_percent == character.fire else Spells.blister
        # magentaprint("SmartCombat favourite_spell is \'" + self.favourite_spell + "\'.")  # works
        self.character = character
        self.regex_cart.extend([RegexStore.prompt, RegexStore.weapon_break, RegexStore.weapon_shatters])

    def notify(self, regex, M_obj):
        # Notifications are used for healing
        # So SmartCombat needs to be registered/unregistered... or have a boolean for whether we're in combat.
        # I prefer the latter.
        super().notify(regex, M_obj)
        if regex in RegexStore.prompt:
            if self.in_combat and self.needs_heal():
                self.use.spam_pots()
            elif not self.needs_heal():
                self.use.stop()
        elif regex in RegexStore.weapon_break or regex in RegexStore.weapon_shatters:
            magentaprint("SmartCombat weapon break: " + str(M_obj.group('weapon')))
            self.broken_weapon = M_obj.group('weapon')

    def needs_heal(self):
        # return self.character.HEALTH < 50  # Test!
        if self.character.mobs.damage:
            return self.character.HEALTH <= max(self.character.mobs.damage)
        else:
            return self.character.HEALTH < 0.25 * self.character.maxHP

    def stop(self):
        self.use.stop()
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

        self.use_any_fast_combat_abilities()  # ie. Touch, Dance

        while not self.stopping:
            if self.broken_weapon:
                self.reequip_weapon()
            # magentaprint("SmartCombat loop kill.timer " + str(round(self.kill.wait_time(), 1)) + " cast.timer " + str(round(self.cast.wait_time(), 1)) + ".")
            if self.kill.up() or self.kill.wait_time() <= self.cast.wait_time() or not self.casting:
                self.kill.wait_until_ready()
                if self.stopping: 
                    break 
                self.use_slow_combat_ability_or_attack()
                # magentaprint("SmartCombat finished attack, stopping: " + str(self.stopping))
                # time.sleep(0.1)  
            else:
                self.cast.wait_until_ready()
                damage = self.character.maxHP - self.character.HEALTH
                if self.stopping:
                    continue
                elif not self.black_magic and ((self.character.MANA >= 2 and damage > self.prompt.max_vigor()) or \
                     (self.character.MANA >= self.character.maxMP - 1 and damage > self.prompt.max_vigor()/1.7)):
                     # (self.character.MANA >= self.character.maxMP - 1 and damage > self.prompt.max_vigor()/1.7 and damage > self.prompt.hptick()):
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
                    else:
                        magentaprint("SmartCombat " + str(self.target) + " in turn targets " + str(a.valid_targets))

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

    def use_slow_combat_ability_or_attack(self):
        for a in self.slow_combat_abilities:
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
        # vigor_cost = 2

    def reequip_weapon(self):
        # Tries to wield all weapons with the same name from inventory
        magentaprint('SmartCombat.reequip_weapon()... broken, weapons1/2: ' + self.broken_weapon + ', ' + self.character.weapon1 + '/' + self.character.weapon2)
        ref = self.character.inventory.get_reference(self.broken_weapon, 2)
        if ref == None:
            return
        if self.character.weapon1 == self.broken_weapon:
            # ref = self.character.inventory.get_reference(self.broken_weapon)
            self.wield.execute(ref)
            self.wield.wait_for_flag()
            if self.wield.success:
                self.broken_weapon = False
                return True
            while self.wield.broken_error:  # found broken one from inventory... this is probably pretty rare
                # need to try the next one
                ref_split = ref.split(' ')
                ref = ref_split[0] + ' '+ str(int(ref_split[1]) + 1)
                if self.character.inventory.get_item_name_from_reference(ref) == self.broken_weapon:
                    self.wield.execute(ref)
                    self.wield.wait_for_flag()
                    if self.wield.success:
                        self.broken_weapon = False
                        return True
                else:
                    # Ran through all items with the same name
                    return False
            if (self.wield.already_wielding_error and self.character.weapon1 == self.character.weapon2) or \
               (self.character.weapon2 == self.broken_weapon):
                self.wield.second.execute(ref)
                self.wield.second.wait_for_flag()
                if self.wield.second.success:
                    self.broken_weapon = False
                    return True
                while self.wield.second.broken_error:
                    ref_split = ref.split(' ')
                    ref = ref_split[0] + ' '+ str(int(ref_split[1]) + 1)
                    if self.character.inventory.get_item_name_from_reference(ref) == self.broken_weapon:
                        self.wield.second.execute(ref)
                        self.wield.second.wait_for_flag()
                        if self.wield.second.success:
                            self.broken_weapon = False
                            return True
                    else:
                        # Ran through all items with the same name
                        return False
                # if self.wield.second.already_wielding_error:
                #     magentaprint('SmartCombat.reequip_weapon wierd case already had weapons.')
                #     self.broken_weapon = False
                #     return True
            # elif self.wield.already_wielding_error:
            #     magentaprint('SmartCombat.reequip_weapon wierd case already had weapon.')
            #     self.broken_weapon = False
            #     return True
            # else:
            #     magentaprint('SmartCombat.reequip_weapon error case.')
            #     return False
        # elif self.character.weapon2 == self.broken_weapon:
        #     # seconding a different weapon
        #     self.wield.second.execute(self.broken_weapon)
        #     self.wield.second.wait_for_flag()
        #     if self.wield.second.success:
        #         self.broken_weapon = False
        return False

        ### Old combat
        # black_magic_spell_cost = self.character.SPELL_COST
        
        # self.buff_up()
        # self.do_combat_skills(monster)

        # magentaprint("Engage: " + monster)
        # ifled = False

        # self.commandHandler.user_kk(monster)
        # self.sleep(0.5)  # Keeps attacking and magic out of sync

        # while(self.commandHandler.KillThread != None and self.commandHandler.KillThread
        #       and self.commandHandler.KillThread.stopping == False):

        #     if(BotThread.can_cast_spell(self.character.MANA, black_magic_spell_cost, self.character.BLACK_MAGIC)):
        #         if(self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
        #             magentaprint("Starting black magic cast thread: " + monster)
        #             self.commandHandler.user_cc(self.character.FAVOURITE_SPELL + " " + monster)
        #         else:
        #             self.commandHandler.stop_CastThread()
            
        #     # TODO: restoratives (use when vig not keeping up or low mana)
        #     if (not self.has_ideal_health()):

        #         self.do_heal_skills()
                
        #         if (BotThread.can_cast_spell(self.character.MANA, vigor_cost, self.character.KNOWS_VIGOR)):
        #             if( self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
        #                 magentaprint("Starting vigor cast thread")
        #                 self.commandHandler.user_cc("vig")
        #         else:
        #             self.commandHandler.stop_CastThread()
        #         #else:
        #             #self.use_restorative_items()


        #     ifled = False
        #     # FLEE Checks
        #     if(self.character.HEALTH <= self.character.HEALTH_TO_FLEE):
        #         # We're done for!  Trust CommandHandler to get us out.  
        #         # It will turn around and stop botThread.
        #         self.do_flee_hook()
        #         ifled = True

        #         # OK the mob died or ran
        #         self.commandHandler.stop_CastThread() 

        #     self.sleep(0.05)   

