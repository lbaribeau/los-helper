
from threading import Thread

from combat.CombatObject import CombatObject
# from Ability import HealAbility, FastCombatAbility, CombatAbility, DanceOfTheCobra, Circle, Bash, Turn, Touch
from command.Ability import *
from misc_functions import magentaprint
import comm.Spells as Spells
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
from command.potion_thread import PotionThreadHandler

class SmartCombat(CombatObject):
    black_magic = True

    def __init__(self, kill, cast, potion_thread_handler, wield, telnetHandler, character, weapon_bot, prompt, info):
        super().__init__(telnetHandler)
        self.thread   = None
        self.target   = None
        self.stopping = None
        self.broken_weapon = ''
        self.activated = False
        self.kill  = kill
        self.cast  = cast
        self.wield = wield
        self.potion_thread_handler = potion_thread_handler
        #self.wear = Wear(character, telnetHandler)
        self.abilities = character._class.abilities.values()

        # self.heal_abilities = [a for a in self.abilities if isinstance(a, HealAbility)]
        # # self.heal_abilities_that_fail = [a for a in self.abilities if isinstance(a, HealAbility) and isinstance(a, AbilityWithFailure)]
        # self.fast_combat_abilities = [a for a in self.abilities if isinstance(a, FastCombatAbility)]
        # self.combat_abilities = [a for a in self.abilities if isinstance(a, CombatAbility)]
        self.heal_abilities        = character._class.heal_skills
        self.buff_abilities        = character._class.buff_skills
        self.slow_combat_abilities = character._class.slow_combat_skills
        self.fast_combat_abilities = character._class.fast_combat_skills

        # spell_percent = max(character.earth, character.wind, character.fire, character.water)
        spell_percent = max(info.spell_proficiencies.values())
        # magentaprint("SmartCombat info.pty " + str(info.pty))
        self.black_magic = info.pty < 7 or spell_percent >= 5
        # self.favourite_spell = Spells.vigor if not self.black_magic else \
        if spell_percent == 0 and self.black_magic:
            self.favourite_spell = Spells.rumble if Spells.rumble in info.spells else \
                                   Spells.hurt if Spells.hurt in info.spells else \
                                   Spells.burn if Spells.burn in info.spells else \
                                   Spells.blister
        else:
            self.favourite_spell = Spells.rumble if spell_percent == info.earth else \
                                   Spells.hurt if spell_percent == info.wind else \
                                   Spells.burn if spell_percent == info.fire else \
                                   Spells.blister
        # magentaprint("SmartCombat favourite_spell is \'" + self.favourite_spell + "\'.")  # works
        self.character = character
        self.regex_cart.extend([
            R.prompt, 
            R.weapon_break, 
            R.weapon_shatters, 
            R.mob_attacked, 
            R.armour_breaks,
            R.mob_arrived, 
            R.mob_wandered, 
            R.mob_left
        ])
        self.mob_target_determinator = MobTargetDeterminator()
        # We can let SmartCombat do a few extra things, like make kill/cast/use commands, but let's not go overboard.
        # Let the parent make WeaponBot.  I think the parent should make use of an Initializer.
        self.weapon_bot = weapon_bot
        self.set_pot_thread = False
        self.healing_spell='v' 
        # command handler can change this
        # Right now human can hit 'cc m' to switch the spell to mend
        # I think command handler needs to be able to hit self.black_magic, in theory
        # Maybe not... just support 'cc m' and 'cc v'
        # With the entire words...
        # So nevermind a target right... well we have kk2... then they could hit kkc to switch it
        # That'll do...
        self.full_rings = False
        self.prompt = prompt
        self.info = info

    def notify(self, regex, match):
        # Notifications are used for healing
        # So SmartCombat needs to be registered/unregistered... or have a boolean for whether we're in combat.
        # I prefer the latter.
        # magentaprint("SmartCombat notify " + match.re.pattern) # gets prompt (too many prints)
        super().notify(regex, match)
        if regex in R.prompt:
            if self.activated:
                if self.should_use_heal_ability():
                    self.heal_abilities[0].execute()
                elif self.needs_heal():
                    # if self.weapon_bot.broken_weapon or not self.character.inventory.has_restorative():
                    if not hasattr(self.weapon_bot, 'weapon') or not self.character.inventory.has_restorative():
                        self.fleeing = True  # TODO: Do pots interfere with the flee timer?  (Should I use a pot?)
                    self.spam_pots()
                else:
                    self.stop_pots_if_started_by_smart_combat()
        # elif regex in itertools.chain(self.end_combat_regexes) and self.activated:
        elif self.end_combat and self.activated:  # requires super() to be called
            self.potion_thread_handler.stop()
            self.activated = False
            # self.check_rings()
        elif regex in R.mob_attacked and self.needs_heal() and not self.character.inventory.has_large_restorative():
            magentaprint("SmartCombat.fleeing = True")
            self.fleeing = True
        elif regex in R.weapon_break + R.weapon_shatters:
            magentaprint("SmartCombat weapon break: " + str(match.group('weapon')))
            # self.broken_weapon = match.group('weapon')
            self.weapon_bot.combat_rewield()
        elif regex in R.armour_breaks:
            magentaprint("SmartCombat armour break: " + str(match.group(1)) + ', len ' + str(len(match.group(1).split(' '))))
            if len(match.group(1).split(' ')) >= 2:
                if match.group(1).split(' ')[1] == 'ring':
                    self.broke_ring = True
        elif regex in R.mob_arrived:
            self.target = self.mob_target_determinator.on_mob_arrival(
                self.target,
                self.character.mobs.read_mobs(match.group('mobs')),
                self.character.mobs.list
            )
            # magentaprint("SmartCombat mob arrived, new target: " + str(self.target))
        elif regex in R.mob_wandered + R.mob_left:
            self.target = self.mob_target_determinator.on_mob_departure(
                self.target,
                self.character.mobs.read_match(match),
                self.character.mobs.list
            )
            pass
        # magentaprint("SmartCombat notify done " + match.re.pattern)

    def notify_of_buffer_completion():
        pass
        # Ok we need to tell MudReaderThread to call this
        # That will be our way of checking if the mob died or didn't after one hit
        # (Wait for all notifies to finish before sending cast)
        # It'll usually work... we could shorten "Your attack overwhelms" to help with clumping

    def stop(self):
        super().stop()
        self.activated = False
        # Eh should we stop the potion thread?
        # sure
        self.potion_thread_handler.stop

    def should_use_heal_ability(self):
        return \
            len(self.heal_abilities) > 0 and \
            self.heal_ability_is_up and \
            self.prompt.hp <= self.info.maxHP - 0.9*self.heal_abilities[0].max_amount

    def needs_big_heal(self):
        return self.potion_threshold() - self.prompt.hp > 6

    def needs_heal(self):
        return self.potion_threshold() - self.prompt.hp > 0
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
        self.potion_thread_handler.stop()
        #self.stopping = True
        super().stop() #.stopping

    def keep_going(self, target=None):
        # self.stopping = False
        # self.casting = True
        # Leave casting how it is, just let the thread continue
        self.set_target(target)
        super().keep_going()

    def start_thread(self, target, spell=None):
        # Doesn't ThreadingMixin do this?
        self.set_target(target)
        self.spell = spell if spell else self.favourite_spell
        magentaprint("SmartCombat spell set to " + str(self.spell))
        self.set_pot_thread = False
        self.kill.stop()
        self.cast.stop()
        # if self.thread is None or not self.thread.is_alive():
        if self.thread and self.thread.is_alive():
            self.keep_going(target)
        else:
            # not is_alive() means it won't look at stopping anymore so we're good.
            self.thread = Thread(target = self.run)
            self.thread.start()

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
        self.stopping    = False
        self.mob_charmed = False
        self.circled     = False
        self.activated   = True
        self.fleeing     = False
        self.error       = False
        self.casting = self.black_magic or Spells.vigor in self.character.spells
        cast = self.cast
        kill = self.kill

        self.use_any_fast_combat_abilities()  # ie. Touch, Dance
        while not self.stopping and not self.end_combat:
            # if self.broken_weapon:
            #     self.reequip_weapon()  # TODO: This can get spammed... answer on to unset is_usable on weapon objects in inventory
            # magentaprint("SmartCombat loop kill.timer " + str(round(self.kill.wait_time(), 1)) + " cast.timer " + str(round(self.cast.wait_time(), 1)) + ".")
            # if self.weapon_bot.broken_weapon:
            #     self.weapon_bot.combat_rewield()
            # Why not call rewield on reaction
            if self.fleeing and not cast.wait_time() - kill.wait_time() > kill.cooldown_after_success:
                # If the cast wait time is so long that we should hit once before fleeing, don't flee yet
                self.escape()
            elif kill.up() or kill.wait_time() <= cast.wait_time() or not self.casting:
                kill.wait_until_ready()
                if self.stopping:
                    break
                self.prompt.clear()
                self.use_slow_combat_ability_or_attack()
                magentaprint("Smart combat attacked, end combat is {}, stopping is {}".format(self.end_combat, self.stopping))
                self.prompt.wait() # Wait for prompt to come to give time for mob death info to get through
                # magentaprint("SmartCombat finished attack, stopping: " + str(self.stopping))
                # time.sleep(0.1) # How do we wait to know if the mob was killed. (Wait for prompt)
                magentaprint("After prompt wait, end combat is {}, stopping is {}".format(self.end_combat, self.stopping))
            else:
                C = self.character
                damage = C.maxHP - C.HEALTH
                cast.wait_until_ready()
                if self.stopping:
                    break
                elif not self.black_magic and \
                    C.MANA >= 2 and \
                    (damage >= C.max_vigor() or (C.MANA >= C.maxMP and damage > C.max_vigor()*0.75)):
                    if damage >= C.max_mend() + C.hp_tick and C.MANA >= 5:
                        self.do_cast('m')
                    else:
                        self.do_cast('v')
                     # (C.MANA >= C.maxMP - 1 and damage > C.max_vigor()/1.7 and damage > C.hp_tick):
                    # TODO: cast vigor if a tick is about to come and we're full mana
                    # (This doesn't consider healing teammates: cc will turn off smart combat for manual teammate healing)
                elif self.mob_charmed:
                    time.sleep(min(0.2, kill.wait_time()))
                    # time.sleep(min(0.2, kill.wait_time() + 0.05))
                    # This should check if there are other mobs fighting and target them... that's kind of out of scope of taking down one target though
                elif self.black_magic and \
                    ((self.spell in Spells._lvl1 and C.MANA >= 3) or (self.spell in Spells._lvl2 and C.MANA >= 7)):  # Todo: add oom check
                    self.do_cast(self.spell, self.target)
                elif self.black_magic and self.spell in Spells._lvl2 and C.MANA < 7 and C.MANA >= 3:
                    self.do_cast(Spells._lvl1[Spells._lvl2.index(self.spell)], self.target)
                else:
                    time.sleep(min(0.2, kill.wait_time()))

        self.activated = False
        magentaprint(str(self) + " ending run().")

    def do_cast(self, spell, target=None):
        self.prompt.clear()
        self.cast.persistent_cast(spell, target)
        self.prompt.wait()
        if self.cast.error:
            self.error = True
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
                    self.error = True
                    self.stop()
                # if self.stopping:
                #     return
                break

    def use_slow_combat_ability_or_attack(self):
        for a in self.slow_combat_abilities + [self.kill]:
            if a.up():
                if isinstance(a, Bash):
                    continue  # For now, don't bash

                if isinstance(a, Circle):
                    # Sets up alternating circling
                    if self.circled:
                        self.circled = False
                        # Todo: execute circle
                        continue
                    else:
                        self.circled = True

                magentaprint("SmartCombat executing " + str(a))
                a.execute(self.target)
                # self.kill.start_timer()
                a.wait_for_flag()
                if a.error:
                    self.error = True
                    self.stop()
                return

        # # self.attack_wait()
        # # self.kill.execute(self.target)
        # # self.kill.wait_for_flag()
        # self.kill.execute_and_wait(self.target) # Wait here please??? Thank you 

        # # magentaprint("Debugging smart combat should catch kill.error: {0}".format(self.kill.error))
        # if self.kill.error:
        #     self.error = True
        #     self.stop()
        # # self.character.ATTACK_CLK = time.time()  # TODO: Kill should be smart enough to keep the clock set
        #                                          # Kill should actually own the clock...

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
        self.wield.execute_and_wait(ref)
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
        # I don't think this gets used... it doesn't look good though
        magentaprint("SmartCombat.reequip_weapon()... broken, weapons1/2: '" + self.broken_weapon + "', '" + self.character.weapon1 + "'/'" + self.character.weapon2 + "'")
        ref = self.character.inventory.get_reference(self.broken_weapon, 2)
        if ref == None:
            return False
        if self.character.weapon1 == self.broken_weapon:
            # ref = self.character.inventory.get_reference(self.broken_weapon)
            self.wield.execute_and_wait(ref)
            # self.wield.wait_for_flag()
            if self.wield.success:
                self.broken_weapon = False
                return True

            while self.wield.failure:  # found broken one from inventory...
                # need to try the next one
                ref = self.mob_target_determinator.increment_ref(ref)
                if self.character.inventory.get_item_name_from_reference(ref) == self.broken_weapon:
                    self.wield.execute_and_wait(ref)
                    # self.wield.wait_for_flag()
                    if self.wield.success:
                        self.broken_weapon = False
                        return True

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
        self.potion_thread_handler.stop()

        if self.character.weapon1 != "":
            self.wield.execute(self.character.inventory.get_last_reference(self.character.weapon1))
        if self.character.weapon2 != "":
            self.wield.second.execute(self.character.inventory.get_last_reference(self.character.weapon2))

    def check_rings(self):
        # magentaprint("SmartCombat check_rings()")
        # if self.broke_ring or not self.full_rings:
            # self.telnetHandler.write('wear all')
        ring_ref = self.character.inventory.first_usable_ring_ref()
        while ring_ref and (self.broke_ring or not self.full_rings):
            # self.telnetHandler.write('wear ' + ring_ref)
            self.wear.execute_and_wait(ring_ref) # This will set it as broken
            # This may not be reliable since it assumes we already know if a ring is broken.
            # No biggie really.  One alternative is to have two 'stopping' variables, since we want to wear rings
            # after the mob dies but maybe not after the player calls stop.
            # However, this solution might work most of the time.
            if self.wear.result in R.no_room:
                self.full_rings = True
                self.broke_ring = False
            # If the ring was broken, the loop should exit by itself (won't come back as usable)
            # If we wore it, then it's no longer in the inventory (won't come up in inventory)
            ring_ref = self.character.inventory.first_usable_ring_ref()

    def spam_pots(self):
        self.set_pot_thread = True
        if self.needs_big_heal():
            self.potion_thread_handler.spam_pots(prefer_big=True)
        else:
            self.potion_thread_handler.spam_pots()

    def stop_pots_if_started_by_smart_combat(self):
        if self.set_pot_thread:
            self.potion_thread_handler.stop()
        self.set_pot_thread = False

#  SmartCombat will have to wait for the DB!!!
# Alternatives: Split WeaponBot into itself and SimpleWeaponBot doesn't work because SmartCombat is supposed to rewield any
# possible weapon, which requires a DB search.  Ugh, it doesn't feel right.  How about just the rewield function fails.  When
# the map is ready, WeaponBot gets set.