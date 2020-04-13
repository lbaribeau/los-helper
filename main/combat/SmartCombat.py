
from threading import Thread

from combat.CombatObject import CombatObject
# from Ability import HealAbility, FastCombatAbility, CombatAbility, DanceOfTheCobra, Circle, Bash, Turn, Touch
from command.Ability import *
from misc_functions import magentaprint
import comm.Spells as Spells
from comm import RegexStore
from combat.Kill import Kill
from combat.Cast import Cast
from command.Use import Use
from command.Wield import Wield
from combat.mob_target_determinator import MobTargetDeterminator
from db.Mob import Mob

class SmartCombat(CombatObject):
    black_magic = True

    def __init__(self, telnetHandler, character, weapon_bot):
        super().__init__(telnetHandler)
        self.thread = None
        self.target = None
        self.mob_target = None
        self.target_fullref = None
        self.stopping = None
        self.broken_weapon = ''
        self.activated = False
        self.kill = Kill(telnetHandler)
        self.cast = Cast(telnetHandler)
        self.use = Use(character, telnetHandler)
        self.wield = Wield(character, telnetHandler)
        # self.wear = Wear(character, telnetHandler)
        self.abilities = character._class.abilities.values()

        # self.heal_abilities = [a for a in self.abilities if isinstance(a, HealAbility)]
        # # self.heal_abilities_that_fail = [a for a in self.abilities if isinstance(a, HealAbility) and isinstance(a, AbilityWithFailure)]
        # self.fast_combat_abilities = [a for a in self.abilities if isinstance(a, FastCombatAbility)]
        # self.combat_abilities = [a for a in self.abilities if isinstance(a, CombatAbility)]
        self.heal_abilities = character._class.heal_skills
        self.buff_abilities = character._class.buff_skills
        self.slow_combat_abilities = character._class.slow_combat_skills
        self.fast_combat_abilities = character._class.fast_combat_skills

        self.character = character
        # spell_percent = max(character.earth, character.wind, character.fire, character.water)
        spell_percent = max(character.spell_proficiencies.values())
        # magentaprint("SmartCombat character.pty " + str(character.pty))
        self.black_magic = character.info.pty < 7 or spell_percent >= 5 or character.PREFER_BM
        # self.favourite_spell = Spells.vigor if not self.black_magic else \    
        self.favourite_spell = self.get_low_rank_spell()

        # magentaprint("SmartCombat favourite_spell is \'" + self.favourite_spell + "\'.")  # works
        self.regex_cart.extend([
            RegexStore.prompt, RegexStore.weapon_break, RegexStore.weapon_shatters, RegexStore.mob_attacked, RegexStore.armour_breaks,
            RegexStore.mob_arrived, RegexStore.mob_wandered, RegexStore.mob_left, RegexStore.not_here
        ])
        self.mob_target_determinator = MobTargetDeterminator()
        # We can let SmartCombat do a few extra things, like make kill/cast/use commands, but let's not go overboard.
        # Let the parent make WeaponBot.  I think the parent should make use of an Initializer.
        self.weapon_bot = weapon_bot
        self.set_pot_thread = False

    def notify(self, regex, M_obj):
        # Notifications are used for healing
        # So SmartCombat needs to be registered/unregistered... or have a boolean for whether we're in combat.
        # I prefer the latter.
        super().notify(regex, M_obj)
        if regex in RegexStore.prompt:
            if self.activated:
                if self.should_use_heal_ability():
                    self.heal_abilities[0].execute()
                elif self.needs_heal():
                    if self.weapon_bot.broken_weapon or not self.character.inventory.has_restorative():
                        self.fleeing = True  # TODO: Do pots interfere with the flee timer?  (Should I use a pot?)
                    self.spam_pots()
                else:
                    self.stop_pots_if_started_by_smart_combat()
        # elif regex in itertools.chain(self.end_combat_regexes) and self.activated:
        elif self.end_combat and self.activated:  # requires super() to be called
            self.use.stop()
            self.activated = False
            self.check_rings()
        elif regex in RegexStore.mob_attacked and self.needs_heal():
            magentaprint("SmartCombat.fleeing = True")
            self.fleeing = True
        elif regex in RegexStore.weapon_break or regex in RegexStore.weapon_shatters:
            magentaprint("SmartCombat weapon break: " + str(M_obj.group('weapon')))
            self.broken_weapon = M_obj.group('weapon')
        elif regex in RegexStore.armour_breaks:
            magentaprint("SmartCombat armour break: " + str(M_obj.group(1)) + ', len ' + str(len(M_obj.group(1).split(' '))))
            if len(M_obj.group(1).split(' ')) >= 2:
                if M_obj.group(1).split(' ')[1] == 'ring':
                    self.broke_ring = True
        elif regex in RegexStore.mob_arrived:
            # magentaprint("mob arrived", False)
            # magentaprint('{} {} {}'.format(self.target, self.character.mobs.read_mobs(M_obj.group('mobs')), self.character.mobs.list), False)
            self.target = self.mob_target_determinator.on_mob_arrival(
                self.target,
                self.character.mobs.read_mobs(M_obj.group('mobs')),
                self.character.mobs.list
            )
            # magentaprint('{} {} {}'.format(self.target, self.character.mobs.read_mobs(M_obj.group('mobs')), self.character.mobs.list), False)
        elif regex in RegexStore.mob_wandered + RegexStore.mob_left:            
            # magentaprint("mob left", False)
            # magentaprint('{} {} {}'.format(self.target, self.character.mobs.read_match(M_obj), self.character.mobs.list), False)
            self.target = self.mob_target_determinator.on_mob_departure(
                self.target,
                self.character.mobs.read_match(M_obj),
                self.character.mobs.list
            )
            # magentaprint('{} {} {}'.format(self.target, self.character.mobs.read_match(M_obj), self.character.mobs.list), False)
        elif regex in RegexStore.not_here:
            self.telnetHandler.write("l")
            pass

    def stop(self):
        super().stop()
        self.activated = False

    def should_use_heal_ability(self):
        return len(self.heal_abilities) > 0 and self.heal_ability_is_up and \
            self.character.HEALTH <= self.character.maxHP - 0.9*self.heal_abilities[0].max_amount

    def needs_big_heal(self):
        return self.potion_threshold() - self.character.HEALTH > 6

    def needs_heal(self):
        return self.potion_threshold() - self.character.HEALTH > 0
        # return self.character.HEALTH < 50  # Test!
        # if self.character.mobs.damage:
        #     return self.character.HEALTH <= 1.3*max(self.character.mobs.damage)
        # else:
        #     return self.character.HEALTH < 0.20 * self.character.maxHP
            # This algorithm isn't completely guaranteed and fails on horrible luck, hoping the extra *0.30 and stdev from mob damage
            # gives restoratives enough time to get above the mob's attack damage... if we get hit when below 1.3x, we run
            # (Usually hps > dps, but if hps < dps, we end up running, and if hps << dps, we could die)
            # I could just switch to large restoratives.  How about use mob damage to determine which restoratives.
            # But when do I flee?  Only when out of restoratives?  Sure.  Maybe if no weapon?  Sure.  No mana?  Nope.
            # So it's basically flee if needs_heal and (broken_weapon or no_restoratives or mob_attacked_before_healing_caught_up)
            # How about use health needed to pick the restorative... well time till next mob attack is also relevant...
            # try large restorative if >5 needed
        # Use restoratives starting at 1.3* mob damage.
        # If we get hit while restoratives are 'on', then flee (mob dps > hps)

    def potion_threshold(self):
        if self.character.mobs.damage:
            return 1.3*max(self.character.mobs.damage)
        else:
            return 0.20 * self.character.maxHP

    def stop(self):
        self.use.stop()
        self.stopping = True

    def keep_going(self, target=None):
        self.stopping = False
        self.casting = True
        self.set_target(target)

    def start_thread(self, target, spell=None):
        self.set_target(target)
        self.spell = spell if spell else self.favourite_spell
        magentaprint("SmartCombat spell set to " + str(self.spell))
        self.set_pot_thread = False

        # if self.thread is None or not self.thread.is_alive():
        if self.thread and self.thread.is_alive():
            self.keep_going(target)
        else:
            # not is_alive() means it won't look at stopping anymore so we're good.
            self.thread = Thread(target = self.run)
            self.thread.start()

    def engage_target(self, target_shorthand, monster):
        self.target = target_shorthand
        self.target_fullref = monster

    def set_target(self, target=None):
        if target:
            if len(target.split(' ')) > 1:
                try:
                    self.target = target.split()[0] + ' '+ str(int(target.split(' ')[1]))
                except ValueError:
                    self.target = target.split()[0]
            else:
                self.target = target
        else:
            self.target = None

    def run(self):
        self.stopping = False
        self.mob_charmed = False
        self.circled = False
        self.activated = True
        self.fleeing = False
        self.broke_ring = False
        self.casting = self.black_magic or Spells.vigor in self.character.spells
        is_combat_ready = True
        is_cast_ready = True
        use_combat_ability = True
        mob_target = None
        self.kill.wait_until_ready()
        if self.character._class.id == 'Mag':
            self.cast.wait_until_ready()

        if self.target_fullref is not None and self.character.ACTIVELY_BOTTING:
            self.mob_target = Mob.get_mob_by_name(self.target_fullref)
            use_combat_ability = self.determine_whether_to_use_combat_ability()
            # self.determine_favorite_spell(mob)

        if use_combat_ability:
            self.use_any_fast_combat_abilities()  # ie. Touch, Dance

        while not self.stopping:
            # if self.broken_weapon:
            #     self.reequip_weapon()  # TODO: This can get spammed... answer on to unset is_usable on weapon objects in inventory
            # magentaprint("SmartCombat loop kill.timer " + str(round(self.kill.wait_time(), 1)) + " cast.timer " + str(round(self.cast.wait_time(), 1)) + ".")
            if self.weapon_bot.broken_weapon:
                self.weapon_bot.combat_rewield()
            if self.fleeing and not self.cast.wait_time() - self.kill.wait_time() > self.kill.cooldown_after_success:
                self.escape()
            else:
                if self.character._class.id != 'Mag':
                    if self.kill.up() or self.kill.wait_time() <= self.cast.wait_time() or not self.casting:
                        if self.do_phys_attack(use_combat_ability):
                            break
                    else:
                        if self.do_magic_attack():
                            continue
                else:
                    if self.cast.up() or self.cast.wait_time() <= self.kill.wait_time() or self.casting:
                        if self.do_magic_attack():
                            break
                    else:
                        if self.do_phys_attack(use_combat_ability):
                            continue

        self.activated = False
        magentaprint(str(self) + " ending run.")

    def determine_whether_to_use_combat_ability(self):
        if self.mob_target is not None:
            if self.mob_target.level is not None:
                # magentaprint("ml {} < cl {} - 4 = {}".format(self.mob_target.level, self.character.level, self.mob_target.level < (self.character.level - 4)),False)
                if self.mob_target.level < (self.character.level - 4) and not self.mob_target.is_named:
                    return False
        return True

    # def determine_favorite_spell(self, mob=None):
    #     if self.character._class.id == 'Mag':
    #     return self.get_high_rank_spell()

    def get_low_rank_spell(self):
        character = self.character
        spell_percent = max(character.spell_proficiencies.values())
        
        if spell_percent == 0 and self.black_magic:
            return Spells.rumble if Spells.rumble in character.spells else \
                   Spells.hurt if Spells.hurt in character.spells else \
                   Spells.burn if Spells.burn in character.spells else Spells.blister
        
        return Spells.rumble if spell_percent == character.info.earth else \
                           Spells.hurt if spell_percent == character.info.wind else \
                           Spells.burn if spell_percent == character.info.fire else Spells.blister

    def get_high_rank_spell(self):
        character = self.character
        spell_percent = max(character.spell_proficiencies.values())
        return Spells.crush if spell_percent == character.info.earth else \
                               Spells.dustgust if spell_percent == character.info.wind else \
                               Spells.fireball if spell_percent == character.info.fire else \
                               Spells.waterbolt if spells_percent == character.info.water else self.get_low_rank_spell()

    def do_phys_attack(self, use_combat_ability):
        self.kill.wait_until_ready()
        if self.stopping:
            return True

        self.use_slow_combat_ability_or_attack(use_combat_ability)
        # magentaprint("SmartCombat finished attack, stopping: " + str(self.stopping))
        # time.sleep(0.1)
        return False

    def do_magic_attack(self):
        self.cast.wait_until_ready()

        damage = self.character.maxHP - self.character.HEALTH
        if self.stopping:
            return True
        elif not self.black_magic and ((self.character.MANA >= 2 and damage > self.character.max_vigor()) or \
             (self.character.MANA >= self.character.maxMP - 1 and damage > self.character.max_vigor()/1.7)):
             # (self.character.MANA >= self.character.maxMP - 1 and damage > self.character.max_vigor()/1.7 and damage > self.character.hptick()):
            # TODO: cast vigor if a tick is about to come and we're full mana
            self.do_cast('v')
        elif self.mob_charmed:
            time.sleep(min(0.2, self.kill.wait_time()))
            # time.sleep(min(0.2, self.kill.wait_time() + 0.05))
        elif self.black_magic and ((self.spell in Spells._lvl1 and self.character.MANA >= 3) or
                                   (self.spell in Spells._lvl2 and self.character.MANA >= 7)):  # Todo: add oom check
            self.do_cast(self.spell, self.target)
        elif self.black_magic and self.spell in Spells._lvl2 and self.character.MANA < 7 and self.character.MANA >= 3:
            self.do_cast(Spells._lvl1[Spells._lvl2.index(self.spell)], self.target)
        else:
            time.sleep(min(0.2, self.kill.wait_time()))

        return False

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

                # magentaprint("Using " + str(a))
                a.execute(self.target)
                a.wait_for_flag()
                # magentaprint("SmartCombat finished using ability.")
                # So if we hit with Dance of the Cobra, we should save mana...
                if a.success and isinstance(a, DanceOfTheCobra):
                    self.mob_charmed = True
                elif a.error:
                    self.stop()
                # if self.stopping:
                #     return
                break

    def use_slow_combat_ability_or_attack(self, use_combat_ability):
        if use_combat_ability:
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

    def try_weapons(self, weapon_name_list):
        self.to_repair = []
        magentaprint("SmartCombat try weapons: " + str(weapon_name_list))
        for w in weapon_name_list:
            # magentaprint("SmartCombat trying weapon " + w)
            if self.try_weapon(w):
                return True
        return False

    def try_weapon(self, weapon_name):
        magentaprint("SmartCombat.try_weapon() on " + str(weapon_name))
        ref = self.character.inventory.get_first_reference(weapon_name, 2)
        if ref == None:
            magentaprint("SmartCombat got ref == None for weapon " + weapon_name)
            return False
        self.wield.execute(ref)
        self.wield.wait_for_flag()
        if self.wield.success:
            self.broken_weapon = False
            return True
        elif self.wield.already_wielding_error:
            self.wield.second.execute(ref)
            self.wield.second.wait_for_flag()
            if self.wield.second.success:
                self.broken_weapon = False
                return True
        else:
            while self.wield.broken_error:
                self.to_repair.append(ref)
                ref = self.mob_target_determinator.increment_ref(ref)
                magentaprint("SmartCombat try_weapon ref incremented: " + str(ref))
                magentaprint("weapon_name: " + str(weapon_name) + ", ")
                if self.character.inventory.get_item_name_from_reference(ref) == weapon_name:
                    self.wield.execute(ref)
                    self.wield.wait_for_flag()
                    if self.wield.success:
                        self.broken_weapon = False
                        return True
                    elif self.wield.already_wielding_error:
                        self.wield.second.execute(ref)
                        self.wield.second.wait_for_flag()
                        if self.wield.second.success:
                            self.broken_weapon = False
                            return True
                else:
                    break
        return False

    def wield_weapon(self, weapon_name):
        # reequip_weapon was checking character.weapon1 and character.weapon2 which I don't want to do here
        # self.equip_weapon(self.broken_weapon)
        magentaprint("SmartCombat.equip_weapon()... weapon_name: " + str(weapon_name))
        ref = self.character.inventory.get_reference(weapon_name, 2)
        if ref == None:
            return False
        self.wield.execute(ref)
        self.wield.wait_for_flag()
        if self.wield.success:
            self.broken_weapon = False
            return True
        while self.wield.broken_error:
            ref = self.mob_target_determinator.increment_ref(ref)
            if self.character.inventory.get_item_name_from_reference(ref) == weapon_name:
                self.wield.execute(ref)
                self.wield.wait_for_flag()
                if self.wield.success:
                    self.broken_weapon = False
                    return True
            else:
                return False
        return False

    def reequip_weapon(self):
        # Tries to wield all weapons with the same name from inventory
        # This could likely be made much shorter using equip_weapon()
        magentaprint("SmartCombat.reequip_weapon()... broken, weapons1/2: '" + self.broken_weapon + "', '" + self.character.weapon1 + "'/'" + self.character.weapon2 + "'")
        ref = self.character.inventory.get_reference(self.broken_weapon, 2)
        if ref == None:
            return False
        if self.character.weapon1 == self.broken_weapon:
            # ref = self.character.inventory.get_reference(self.broken_weapon)
            self.wield.execute(ref)
            self.wield.wait_for_flag()
            if self.wield.success:
                self.broken_weapon = False
                return True
            while self.wield.broken_error:  # found broken one from inventory...
                # need to try the next one
                ref = self.mob_target_determinator.increment_ref(ref)
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
                    ref = self.mob_target_determinator.increment_ref(ref)
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

        # self.command_handler.user_kk(monster)
        # self.sleep(0.5)  # Keeps attacking and magic out of sync

        # while(self.command_handler.KillThread != None and self.command_handler.KillThread
        #       and self.command_handler.KillThread.stopping == False):

        #     if(BotThread.can_cast_spell(self.character.MANA, black_magic_spell_cost, self.character.BLACK_MAGIC)):
        #         if(self.command_handler.CastThread == None or not self.command_handler.CastThread.is_alive()):
        #             magentaprint("Starting black magic cast thread: " + monster)
        #             self.command_handler.user_cc(self.character.FAVOURITE_SPELL + " " + monster)
        #         else:
        #             self.command_handler.stop_CastThread()

        #     # TODO: restoratives (use when vig not keeping up or low mana)
        #     if (not self.has_ideal_health()):

        #         self.do_heal_skills()

        #         if (BotThread.can_cast_spell(self.character.MANA, vigor_cost, self.character.KNOWS_VIGOR)):
        #             if( self.command_handler.CastThread == None or not self.command_handler.CastThread.is_alive()):
        #                 magentaprint("Starting vigor cast thread")
        #                 self.command_handler.user_cc("vig")
        #         else:
        #             self.command_handler.stop_CastThread()
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
        #         self.command_handler.stop_CastThread()

        #     self.sleep(0.05)

    def escape(self):
        self.stop()
        self.cast.stop()
        self.kill.stop()
        self.cast.wait_until_ready()
        self.kill.wait_until_ready()

        if self.character.weapon1 != '':
            self.telnetHandler.write("rm " + self.character.weapon1)
        if self.character.weapon2 != '':
            self.telnetHandler.write("rm " + self.character.weapon2)

        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")

        time.sleep(0.1)
        self.stop_pots_if_started_by_smart_combat()
        self.use.stop()

        if self.character.weapon1 != "":
            self.wield.execute(self.character.inventory.get_last_reference(self.character.weapon1))
        if self.character.weapon2 != "":
            self.wield.second.execute(self.character.inventory.get_last_reference(self.character.weapon2))

    def check_rings(self):
        # magentaprint("SmartCombat check_rings()")
        if self.broke_ring:
            # self.telnetHandler.write('wear all')
            ring_ref = self.character.inventory.first_usable_ring_ref()
            if ring_ref:
                self.telnetHandler.write('wear ' + self.character.inventory.first_usable_ring_ref())
                # This may not be reliable since it assumes we already know if a ring is broken.
                # No biggie really.  One alternative is to have two 'stopping' variables, since we want to wear rings
                # after the mob dies but maybe not after the player calls stop.
                # However, this solution might work most of the time.

    def spam_pots(self):
        self.set_pot_thread = True
        if self.needs_big_heal():
            self.use.spam_pots(prefer_big=True)
        else:
            self.use.spam_pots()

    def stop_pots_if_started_by_smart_combat(self):
        if self.set_pot_thread:
            self.use.stop()
        self.set_pot_thread = False

#  SmartCombat will have to wait for the DB!!!
# Alternatives: Split WeaponBot into itself and SimpleWeaponBot doesn't work because SmartCombat is supposed to rewield any
# possible weapon, which requires a DB search.  Ugh, it doesn't feel right.  How about just the rewield function fails.  When
# the map is ready, WeaponBot gets set.