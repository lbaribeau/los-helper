
from threading import Thread

from combat.CombatObject import CombatObject
# from Ability import HealAbility, FastCombatAbility, CombatAbility, DanceOfTheCobra, Circle, Bash, Turn, Touch
from command.Ability import *
from misc_functions import magentaprint
import comm.Spells as Spells
from comm                           import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
from command.potion_thread          import PotionThreadHandler
from reactions.referencing_list     import ReferencingList

class SmartCombat(CombatObject):
    black_magic = True

    def __init__(self, kill, cast, potion_thread_handler, wield, telnetHandler, character, weapon_bot, prompt, info, mud_reader_completion_event, regex_busy):
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
            self.favourite_spell = Spells.rumble if Spells.rumble in character.spells else \
                                   Spells.hurt if Spells.hurt in character.spells else \
                                   Spells.burn if Spells.burn in character.spells else \
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
            R.mob_left,
            R.fighting_white_magic_caster,
            R.fighting_black_magic_caster
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
        self.mud_reader_completion_event = mud_reader_completion_event
        self.regex_busy = regex_busy

    def notify(self, regex, match):
        # Notifications are used for healing
        # So SmartCombat needs to be registered/unregistered... or have a boolean for whether we're in combat.
        # I prefer the latter.
        # magentaprint("SmartCombat notify " + match.re.pattern) # gets prompt (too many prints)
        super().notify(regex, match) # Calls self.stop if it's an end-combat regex (maybe)
        if not self.activated:
            magentaprint("SmartCombat got a notify, but not activated, regex: " + regex[0:20])
        elif regex in R.prompt and self.activated:
            if self.should_use_heal_ability():
                self.heal_abilities[0].execute()
            elif self.needs_heal():
                # if self.weapon_bot.broken_weapon or not self.character.inventory.has_restorative():
                if not hasattr(self.weapon_bot, 'weapon') or not self.character.inventory.has_restorative():
                    self.fleeing = True  # TODO: Do pots interfere with the flee timer?  (Should I use a pot?)
                    magentaprint("SmartCombat fleeing ASAP")
                    print('\a') # Terminal programs interpret this character as being asked to make an alarm sound, so a sound is made so you know bot is low HP
                self.spam_pots()
            else:
                self.stop_pots_if_started_by_smart_combat()
        # elif regex in itertools.chain(self.end_combat_regexes) and self.activated:
        elif self.end_combat and self.activated:  # requires super() to be called
            self.potion_thread_handler.stop()
            self.activated = False
            # self.check_rings()
        elif regex in R.mob_attacked and self.needs_heal() and not self.character.inventory.has_large_restorative():
            self.fleeing = True
            magentaprint("SmartCombat fleeing ASAP (2)")
            print('\a')
        elif regex in R.weapon_break + R.weapon_shatters:
            magentaprint("SmartCombat weapon break: " + str(match.group('weapon')))
            # self.broken_weapon = match.group('weapon')
            self.weapon_bot.combat_rewield()
        elif regex in R.armour_breaks:
            magentaprint("SmartCombat armour break: " + str(match.group(1)) + ', len ' + str(len(match.group(1).split(' '))))
            if len(match.group(1).split(' ')) >= 2:
                if match.group(1).split(' ')[1] == 'ring':
                    self.broke_ring = True
        elif regex in R.mob_arrived and self.activated:
            magentaprint("SmartCombat mob arrived")
            # self.activated prevents unnecessary prints (calls to referencing_list.get)
            self.target = self.mob_target_determinator.on_mob_arrival(
                self.target,
                self.character.mobs.read_mobs(match.group('mobs')),
                self.character.mobs.list
            )
            # magentaprint("SmartCombat mob arrived, new target: " + str(self.target))
        elif regex in R.mob_wandered + R.mob_left and self.activated:
            magentaprint("SmartCombat mob left")
            old_target_ref=self.target
            # RL=ReferencingList(self.character.mobs.list)
            departed_mob_name = self.character.mobs.read_mob_name_from_regex_match(match)
            # RL.add(departed_mob_name), # Departed mob should be in it now
            self.character.mobs.list.add(departed_mob_name), # Departed mob should be in it now
            # (this is some spaghetti though... we are shuffling the list elements!)
            # Could go back to using "RL" but I'm afraid that's slow
            # temp=self.character.mobs.list
            # self.character.mobs.list=RL
            self.target = self.mob_target_determinator.on_mob_departure(
                self.target,
                # Ehrm I presume... the mobs.list... has changed already?????????
                # Who gets notified first???
                # Keep our own version of it?
                # Is the mudreader subscription ordered??
                # Before I had to add the mob back in! 
                # So we have the new list!
                # Ok so we need to put the mob name back in (to a copy of the list)
                # ReferencingList(self.character.mobs.list).add(self.character.mobs.read_mob_name_from_regex_match(match)),
                # RL,
                self.character.mobs.list,
                # self.character.mobs.get_ref_of_attacking_mob(match) 
                # Not actually an attacking mob! but works anyway? Ehhh it uses mob.list!!
                # Need to use a hypothetical mobs.list because mobs.list has changed already
                # RL.get_ref_of_attacking_mob(match, RL) # doesn't have that function
                # Time for a messy hack
                self.character.mobs.get_ref_of_attacking_mob(match) # ie gives "stall 3" from "2nd stall holder" if a "stall bolder" is present
            )
            # self.character.mobs.list = temp
            # del RL
            self.character.mobs.list.remove(departed_mob_name)
            magentaprint("SmartCombat MTD just checked target!: \""+str(old_target_ref)+"\" to \""+str(self.target)+"\"! Wow!")
            # Ok well it can still happen
            # 56.6: "ci miner"
            # 56.7: "The 1st koboled miner just wandered to the east.""
            # (MTD: self.target = """)
            # 56.8: "You failed to circle it"
            # So we need to "queue up" the target edit... maybe we know if "wandered off" comes in before the attack response we know we "missed" (server didn't get message on time)
            # Maybe we should read very eager? 
            # We didn't hit the target we intended... we ended up hitting the 2nd... so MTD makes a good point... 
            # I guess if this case happens while kill or circle is "executing" that'd be a good clue

        elif regex in R.fighting_white_magic_caster:
            self.fighting_white_magic_caster = True
        elif regex in R.fighting_black_magic_caster:
            self.fighting_black_magic_caster = True
        else:
            magentaprint("Some random smartCombat notify() not dealt with or self.activated was false")
        # magentaprint("SmartCombat notify done " + match.re.pattern)

    @property
    def fighting_caster(self):
        return self.fighting_white_magic_caster or self.fighting_black_magic_caster

    def notify_of_buffer_completion():
        pass
        # Ok we need to tell MudReaderThread to call this
        # That will be our way of checking if the mob died or didn't after one hit
        # (Wait for all notifies to finish before sending cast)
        # It'll usually work... we could shorten "Your attack overwhelms" to help with clumping

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
            if len(self.character.mobs.attacking) >= 2:
                return 2.6*max(self.character.mobs.damage)
            else:
                return 1.3*max(self.character.mobs.damage)
        else:
            return 0.25 * self.character.maxHP

    # def stop(self):
    #     super().stop() # Where is stop implemented? It has to set self.stopping? Or does it?? Maybe it's not implemented in super!?
    #     self.activated = False
    #     # Eh should we stop the potion thread?
    #     # sure
    #     self.potion_thread_handler.stop 

    def stop(self):
        self.potion_thread_handler.stop()
        #self.stopping = True
        super().stop() #.stopping (combat/ThreadingMixin.py)

    def keep_going(self, target=None):
        # self.stopping = False
        # self.casting = True
        # Leave casting how it is, just let the thread continue
        self.set_target(target)
        super().keep_going()

    def start_thread(self, target, spell=None):
        # Doesn't ThreadingMixin do this?
        self.set_target(target)
        if spell:
            self.spell = spell 
        else:
            # So target is a string
            # We could have the 'bot' in charge of picking the spell
            # (We want level 2 magic for lvl >= 8 or 9)
            # We need to resolve the target against the mob list
            # I think that smart combat just expects a string
            # Mob list stuff is typically the 'bot's job
            self.spell = self.favourite_spell
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

    def berserking(self):
        # Fixed it:
        if Berserk.command in self.character._class.abilities:
            return self.character._class.abilities[Berserk.command].active
        else:
            return False
        # Needed to put wear_off_regex into regex_cart, and correctly

    def run(self):
        self.stopping    = False
        self.mob_charmed = False
        self.circled     = False
        self.bashed      = False
        self.activated   = True
        self.fleeing     = False
        self.error       = False
        self.casting = self.black_magic or Spells.vigor in self.character.spells
        cast = self.cast
        kill = self.kill
        self.result='' # makes sure self.end_combat isn't True
        self.fighting_white_magic_caster = False
        self.fighting_black_magic_caster = False
        self.end_combat=False

        # magentaprint("SmartCombat Why isn't this wait waiting1")
        # magentaprint(self.mud_reader_completion_event)
        # self.mud_reader_completion_event.clear()
        # self.mud_reader_completion_event.wait()
        # magentaprint("SmartCombat Why isn't this wait waiting2")

        # Set spell based on mob here
        # Mob target isn't set in init, it's set after sometimes
        # Also, start() isn't always called
        # So we assume that self.target is set
        # Also self.spell apparently...
        # Well we have self.target which is a reference
        # So we get the mob full name back
        # And set the spell here, if black magic...
        # Well spell is set in engage_monster with target, that might work better, since 'monster' and target are known there
        # Mob.get_mob_by_name(self.character.mobs.list.get(self.target)) # So is this a list of strings or mobs... Cartography set this up right...

        self.use_any_fast_combat_abilities()  # ie. Touch, Dance
        while not self.stopping and not self.end_combat:
            # if self.broken_weapon:
            #     self.reequip_weapon()  # TODO: This can get spammed... answer on to unset is_usable on weapon objects in inventory
            # magentaprint("SmartCombat loop kill.timer " + str(round(self.kill.wait_time(), 1)) + " cast.timer " + str(round(self.cast.wait_time(), 1)) + ".")
            # if self.weapon_bot.broken_weapon:
            #     self.weapon_bot.combat_rewield()
            # Why not call rewield on reaction
            if self.fleeing and not cast.wait_time() - kill.wait_time() > kill.cooldown_after_success and not self.berserking():
                # If the cast wait time is so long that we should hit once before fleeing, don't flee yet
                # If berserking we just have to keep fighting (leave fleeing true though in case berserk fades)
                self.escape()
            elif kill.up() or kill.wait_time() <= cast.wait_time() or not self.casting:
                magentaprint("SmartCombat kill block")
                kill.wait_until_ready()
                if self.stopping:
                    break
                if self.fleeing and not self.berserking():
                    self.escape() # added recently to improve flee as I felt the bot was not noticing it should flee and issuing an attack, not confirmed though
                    break
                self.prompt.clear()
                self.mud_reader_completion_event.clear()
                self.prompt.clear()
                if self.stopping:
                    break
                self.use_slow_combat_ability_or_attack()
                self.prompt.wait()  # We want, even if the prompt came already... we want this wait to go through, we don't want a clear() at this moment, just to know the prompt came
                # self.mud_reader_completion_event.clear() # How does this work at all... 
                # What if we got the prompt already? In a clump with the attack? Also, we did a list operation to add mob attacking
                # Might be introducing a wait
                # magentaprint("Smart combat attacked, end combat is {}, stopping is {}, event is {}".format(self.end_combat, self.stopping, self.mud_reader_completion_event.is_set()))
                # self.prompt.wait() # Wait for prompt to come to give time for mob death info to get through
                # magentaprint("SmartCombat finished attack, stopping: " + str(self.stopping))
                # time.sleep(0.1) # How do we wait to know if the mob was killed. (Wait for prompt)
                # Oooookkkkkk now we're waiting too long... 
                # magentaprint("After prompt wait, end combat is {}, stopping is {}, event is {}".format(self.end_combat, self.stopping, self.mud_reader_completion_event.is_set()))
                self.mud_reader_completion_event.wait()
                # magentaprint("After mud reader completion, end combat is {}, stopping, {}, event, {}".format(self.end_combat, self.stopping, self.mud_reader_completion_event.is_set()))
                # We have regex_busy now, could use that too
            else:
                # magentaprint("SmartCombat cast block") # Good info but prints too much
                C = self.character
                damage = C.maxHP - C.HEALTH
                cast.wait_until_ready()
                if self.stopping:
                    break
                elif self.fleeing and not self.berserking():
                    self.escape() # added recently to improve flee as I felt the bot was not noticing it should flee and issuing an attack, not confirmed though
                    break
                elif not self.casting or (self.mob_charmed and len(C.mobs.attacking) <= 1):
                    time.sleep(min(0.2, kill.wait_time()))
                    # time.sleep(min(0.2, kill.wait_time() + 0.05))
                    # mob_charmed should check if there are other mobs fighting and switch to them (bot-level logic)
                    # So return if mob_charmed to do that
                    # Here we are just saving the mana (same as not casting)
                elif self.black_magic:
                    if self.spell in Spells._lvl3 and C.MANA < 10:
                        self.do_cast(Spells._lvl1[Spells._lvl3.index(self.spell)], self.target)
                    elif self.spell in Spells._lvl2 and C.MANA < 7:
                        self.do_cast(Spells._lvl1[Spells._lvl2.index(self.spell)], self.target)
                    elif C.MANA >= 3:
                        self.do_cast(self.spell, self.target)
                    else:
                        time.sleep(min(0.2, kill.wait_time())) # Checks mana and fleeing but goes into melee if it's up
                elif C.MANA >= 2:
                    if C.MANA >= 5 and damage >= C.max_mend() + C.hp_tick():
                        self.do_cast('m')
                    elif damage >= C.max_vigor() or (C.MANA >= C.maxMP and damage > C.max_vigor()*0.75):
                        # (C.MANA >= C.maxMP - 1 and damage > C.max_vigor()/1.7 and damage > C.hp_tick()):
                        self.do_cast('v')
                    else:
                        time.sleep(min(0.2, kill.wait_time()))
                    # TODO: cast vigor if a tick is about to come and we're full mana
                    # (This doesn't consider healing teammates: cc will turn off smart combat for manual teammate healing)
                else:
                    time.sleep(min(0.2, kill.wait_time()))

        self.activated = False
        magentaprint(str(self) + f" loop ended, run() ended, exiting (stopping: {self.stopping}, end_combat: {self.end_combat}.")

    def wait_for_one_of_kill_and_cast(self):
        # Grindthread is gonna use these
        magentaprint("SmartCombat kill and cast wait for one: {}s".format(round(max(min(self.kill.wait_time(), self.cast.wait_time()), 0),3)))
        time.sleep(max(min(self.kill.wait_time(), self.cast.wait_time()), 0))

    def wait_for_both_of_kill_and_cast(self):
        # magentaprint("SmartCombat kill and cast wait for both: {}s".format(max(min(self.kill.wait_time(),0), min(self.cast.wait_time(),0))))
        # time.sleep(max(min(self.kill.wait_time(),0), min(self.cast.wait_time(),0)))
        magentaprint("SmartCombat kill and cast wait for both: {}s".format(round(max(self.kill.wait_time(), self.cast.wait_time(),0),3)))
        time.sleep(max(self.kill.wait_time(), self.cast.wait_time(),0))

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
                    magentaprint("SmartCombat saw mob charmed.")
                    self.mob_charmed = True
                elif a.error:
                    self.error = True
                    self.stop()
                # if self.stopping:
                #     return
                break

    def use_slow_combat_ability_or_attack(self):
        kill = self.kill
        for a in self.slow_combat_abilities + [kill]:
            if a.up():
                if isinstance(a, Bash):
                    if not self.fighting_black_magic_caster or len(self.character.mobs.attacking) > 1:
                        continue
                    # Continue means don't use this ability, go to the next one, the last option being regular attack
                    # Don't bash white magic casters, just dps

                    if self.bashed:
                        self.bashed = False
                        continue # ie. we bashed already, so don't bash again (need to dps)
                    else:
                        self.bashed = True
                        self.circled = True # Do not circle if bashing
                elif isinstance(a, Circle):
                    # Optimal group fighting is probably using both circle and bash but not doing that here... 
                    if len(self.character.mobs.attacking) > 1 or self.fighting_caster:
                        # Don't circle casters
                        # Skip circle if many mobs (need to dps)
                        # This didn't work? Had aggro on 2 mobs keps circling... (mobs.attacking wasn't being populated)
                        continue

                    # Sets up alternating circling (1 target)
                    if self.circled:
                        self.circled = False
                        continue # We circled already, do not circle again
                    else:
                        self.circled = True

                magentaprint("SmartCombat calling wait for regex_busy ({})".format(a.__class__)) # We could put this right into telnethandler, right?? Yes... could put it everywhere
                # self.mudReaderThread.MLT.regex_busy.wait() # Just to make sure notifies from Mobs aren't currently happening (ie. MTD - mob target determinator)
                self.regex_busy.wait() # Just to make sure notifies from Mobs aren't currently happening (ie. MTD - mob target determinator)
                # magentaprint("SmartCombat executing ability \"a\" (class" + str(a.__class__)+")") # We'll get a print of the command
                a.execute(self.target) # Ehrm this didn't use to wait, now it waits? Yes... No it doesn't wait but it clears the waiter flag
                # if a.success and not self.stopping and not self.end_combat and a.result not in R.ze_mob_fled + R.ze_mob_died:

                # Be careful of multiple adding... it checks for that...
                magentaprint("SmartCombat execute finished, adding mob attacker ("+str(self.target)+")")
                self.character.mobs.add_attacker_with_ref(self.target)  # Ok this can definitely add AFTER it got removed from fleeing (stopping check should prevent)
                    # Because... how else did it gett added on those two regexes... "You bludgeon for 5". "The acolyte flees"... so we got an add somehow on You bludgeon
                # self.character.mobs.attacking.append(self.target) 
                # Let's assume the mob will retaliate
                # Typically mobs checks to add attackers whenever they attack
                # Suppose another mob attacks too... this way we know right away that there are two attackers
                # Ehrm I think this is taking a millisecond and then we can't wait for prompt
                # The problem is this is happening too late... it gets re-added after the mob flees... 
                # Same with "They are not here" on circle... needs to get removed from attacking
                # Maybe just add it earlier!?               

                # magentaprint("SmartCombat use_slow_combat_ability_or_attack() Mobs attacking by the way: " + str(self.character.mobs.attacking))
                kill.start_timer() # Why commented out? Because those objects should do it themselves?
                kill.timer += 1 # Add 1 for now in case circle failed
                # By the way, failing to circle it has a longer cooldown! (on both kill and circle? Yes)
                a.wait_for_flag() # We will probably wait for the prompt and mud_reader_completion anyway
                # Ok in the lag case self.target is now wrong
                # We could check it?? Why not? Should also fix it for "cast" ideally
                if a.error:
                    self.error = True
                    if a._sent_target in self.character.mobs.attacking:
                        self.character.mobs.attacking.remove(a._sent_target) 
                        # Since we just added it we know we can remove it... also we know nothing removes on this regex
                        # Note that mob fleeing could have "happened" first and edited self.target (not on error though)
                    else:
                        magentaprint("SmartCombat thought it had to remove {} from mobs.attacking?? (attack error)".format(a._sent_target))
                    kill.timer -= 4
                    self.stop()
                    return
                #elif a.failure:
                    # kill.timer is correct
                # elif a.success or not isinstance(a, Circle) or not isinstance(a,Bash):
                elif a.success or isinstance(a, Kill) or isinstance(a, Wither) or isinstance(a, Touch):
                    kill.timer -= 1 # Bash, circle have 4s cooldown on fail... maybe check some of the other abilities? Fail safe?
                    # Not sure about wither and Touch but Circle and Bash have 4s cooldown
                a.timer=kill.timer
                # The point of the above was to implement the common cooldown of "kill" and "circle"
                # If circle fails there's an extra second

                # What if MTD is correcting attacking list and mobs.list as we speak?!?!?
                # Can we wait for MRT?
                # Let MudListener "clear" a flag and MRT "set" it (I hate those terms)
                # self.mudReaderThread.MLT.regex_busy.wait()
                # self.regex_busy.wait() # Just to make sure notifies from Mobs aren't currently happening (ie. MTD - mob target determinator)
                # Why here? We needed it before we sent the command

                # Lag fix... won't catch everything though
                # (Suppose mob leaves and MTD makes our target "" but we actually hit another mob of the same name)
                # if self.target == "" and a.success or a.failure: 
                # Could do it more strongly... 
                # What if it died or fled though??!?
                # Ok this was a good idea but caused a problem... we kept attacking after the mob was gone...
                if self.character.mobs.list.index(self.target) != self.character.mobs.list.index(a._sent_target) and not self.stopping:
                    # Ok we probably hit the wrong thing
                    # The "stopping" check is because we might have killed the mob, and in that case, it's no longer in mobs.list
                    target_from_return_string = self.character.mobs.get_ref_of_attacking_mob(a.M_obj) # Maybe we can see what we hit from the text
                    if target_from_return_string:
                        # Might not work, ie, "You failed to circle it." doesn't have mob name in it
                        # But this is just lag correction
                        self.target = target_from_return_string # Ok good we saw what we hit
                    else:
                        self.target = a._sent_target # Suppose "A mob arrived" at the wrong time... this is our best bet
                        # (This is like "undo" if mob target determinator did something in lag and was too late")
                        # May as well switch back to what we sent even if it missed
                    # if isinstance(s, Kill) or (isinstance
                    # self.target = self.character.mobs.get_ref_of_attacking_mob(a.M_obj)
                # Smart combat doesn't know if the mob died???
                # Combat objects get killed (stopped) by a reaction
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
        weapon_bot = self.weapon_bot
        if hasattr(weapon_bot,'weapon'):
            w1=weapon_bot.weapon
        else:
            w1=self.character.weapon1

        if ref == None:
            return False
        if w1 == self.broken_weapon:
            # ref = self.character.inventory.get_reference(self.broken_weapon)
            self.wield.execute_and_wait(ref)
            # self.wield.wait_for_flag()
            if self.wield.success:
                self.broken_weapon = False
                return True

            while self.wield.failure:  # found broken one from inventory...
                # need to try the next one
                # Why would this ever work? Broken weapon will be at back of stack
                ref = self.mob_target_determinator.increment_ref(ref)
                if self.character.inventory.get_item_name_from_reference(ref) == self.broken_weapon:
                    self.wield.execute_and_wait(ref)
                    # self.wield.wait_for_flag()
                    if self.wield.success:
                        self.broken_weapon = False
                        return True

            if (self.wield.already_wielding_error and w1 == self.character.weapon2) or \
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

        # w1=self.character.weapon1
        w2=self.character.weapon2
        weapon_bot=self.weapon_bot
        if hasattr(weapon_bot, 'weapon'):
            w1=self.weapon_bot.weapon # weapon_bot is new, need to use it instead of character.weaponX
        else:
            w1=''

        # Removed leather cap instead of leather whip(!)
        # self.character.equipment.get_ref_of_item_by_slot('wielded')

        if w1 != '':
            self.telnetHandler.write("rm " + w1)  # Could split off second word, ie. "mace" in "small mace"
            # self.telnetHandler.write("rm " + self.character.equipment.get_ref_of_item_by_slot('wielded')) # I don't think this works
            # Could use "Remove" command... inventory might get messed up...
        if w2 != '':
            self.telnetHandler.write("rm " + w2)
            # self.telnetHandler.write("rm " + self.character.equipment.get_ref_of_item_by_slot('seconded')) # I don't think this works

        # self.character.TRYING_TO_MOVE=True # Such that cartography matches the area we get to... maybe flee should be a Command object
        # NOPE JANKY (You run like a chicken gets matched)
        self.character.LAST_DIRECTION="fleeing" # If we get a dark area, this variable would have been the previous "go", which Cartography uses to guess where we went
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")

        ## Ehrm after we flee we should figure out where we are
        ## Referring to Cartography,
        # self.character.TRYING_TO_MOVE = True
        # prev_area = self.character.AREA_ID
        # self.cartography.clear() # Referring to Go (Go.py does this) (this means wait for a notify event to finish ie. server text)
        # # Some of this might need to be at a bot level oy since we don't have access to cartography?? Also it's not really combat??
        # # Could return saying we fled or return saying to flee
        # # To wherever smart combat is called from... that's a thread handoff
        # # so need to call cartography.wait()
        # self.cartography.wait(timeout=3) # to get new area ID (Prefers that flee will work...) https://docs.python.org/3/library/threading.html#threading.Event.wait
        # new_area = self.character.AREA_ID
        # # Now find path from where we are to where we were...
        # self.mud_map.get_path(new_area, prev_area) # like from GotoThread
        # # Ok wait a minute is our answer really to go back there... why didn't we just walk away??? is that possible?
        # # What if it blocks
        # # Well... ideally we find a place to rest at I guess
        # The fact is we died because we got lost... so it's better to repair the path... maybe add a rest after fleeing


        # Maybe use remove command if it exists? Fleeing is kind of panic-mode... also this might work

        # time.sleep(0.1)
        time.sleep(0.9) # Needs to be long enough for inventory to realize weapon was removed... else we do it properly with a Command object but that's too slow
        # (get_last_reference is None if Inventory doesn't have "small mace" in it)
        # So it doesn't get rewielded... code write code that "assumes" it's in inventory if needed 
        self.stop_pots_if_started_by_smart_combat()
        self.potion_thread_handler.stop()

        if w1 != '':
            self.wield.execute_and_wait(self.character.inventory.get_last_reference_with_print(w1))
        if w2 != '':
            self.wield.second.execute_and_wait(self.character.inventory.get_last_reference_with_print(w2))

        # Alright well SmartCombat should return a code maybe the bot can reconstruct the path... a safe path... or rest on the spot??? That'd be good
        # Currently it tries to continue and messes up where it is
        # So it tries to go to exits that don't exist etc.
        # Till it runs out of directions
        # "I don't see that exit."
        # "You can't go that way"
        # One is "error" one is "failure" yeesh
        # Then from there we get "CAUTION: decide_where_to_go called when we should be in the chapel"
        # It says "l" unnecessarily I think
        # Would a rest really be good? Might we get attacked by a hostile?? A fresh one? Is status quo ok? 

        # I think I had a bug of using self.character.weapon1 when I should start using weapon_bot (hasattr(weapon_bot), 'weapon')
        # So I didn't rewield (blank rewield)

        # Now this needs, on command sent, save current location
        # After that 0.9, get current location again - maybe use go to determine it?Needs Trying to Move?
        # Anyway after that you need to fix direction list?
        # Yea because otherwise we end up back in combat with a bad direction list that could think we're in the pawn shop?
        # I guess we fled North to Holly Lane... would have been good to rest up (7 hp)
        # Could we just kind of hit Go so we can use it for area regex notify... there are a bunch of race conditions we want to know where we are
        # We also need to know how to make a path! Try command handler goto or showto

        # FLEE RECOVERY
        # we have self.fleeing is true and SmartCombat exits
        # So where was smartcombat started?
        # Do we add code there?
        # Ok...
        # The follow-up is in engage_monster



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

    # def get_mob_level(self):
        # Uses self.target and self.character.mobs.list to ask the DB for mob level
        # To choose spell with (or is that too "smart")
        # No we wrote Mob.get_mob_level_from_name()
        # I put spell choice in engage_monster where spell is set

    def fight(self, target):
        magentaprint("SmartCombat engaging"+target+"!")
        self.target = target
        self.set_pot_thread = False
        self.run()
        magentaprint("SmartCombat completed!")



    # def berserking(self):
    #     if hasattr(self, "berserk_ability"):
    #         return self.berserk_ability.active

    #     magentaprint("Smart combat looking at abilities... ")
    #     magentaprint(str(self.character._class.abilities))
    #     for a in self.character._class.abilities:
    #         # magentaprint("Smart combat looking at abilities... " + a.command)
    #         magentaprint("Smart combat looking at abilities... " + str(a))
    #         magentaprint(a.__class__)
    #         magentaprint(isinstance(a, Berserk))
    #         if isinstance(a, Berserk):
    #             magentaprint("Got Berserk ability")
    #             self.berserk_ability=a
    #             break

    #     if Berserk.command in self.character._class.abilities:
    #         self.berserk_ability=a

    #     if hasattr(self, "berserk_ability"):
    #         return self.berserk_ability.active
    #     else:
    #         # self.berserk_ability=BuffAbility(self.telnetHandler)
    #         # Ack this isn't working
    #         # init assumes there are success regexes
    #         # self.berserk_ability=object()
    #         # self.berserk_ability.active=False # doesn't work
    #         class DummyAbility(BuffAbility):
    #             active=False
    #             # wear_off_regex=RegexStore.red_mist_fades
    #             def __init__(self, telnetHandler):
    #                 self.success_regexes=[]
    #                 self.error_regexes=[]
    #                 super().__init__(telnetHandler)
    #         self.berserk_ability=DummyAbility(self.telnetHandler) # Object that always says "active" is False
    #         # Question though - how did we get to this section as a barbarian...
    #         # So, expecting the error... can't run if you are berserk... (unlikely)
    #         # ...Ok maybe I know why this didn't work either?
    #         # Maybe because it never happens
    #         # We were still using actual Berserk
    #         # Ok that's good so we know why Dummy also didnt' work
    #         # I fixed Berserk. Wear_off_regex needed to be in regex_cart to get notification. Also, += was weird because strings, .append worked...
    #         # Also be sure to use "in" because everything in the regex store is in lists

    #     return self.berserk_ability.active
    #     # Could be better if were to notice right away when berserking drops but that's an optimization



#  SmartCombat will have to wait for the DB!!!
# Alternatives: Split WeaponBot into itself and SimpleWeaponBot doesn't work because SmartCombat is supposed to rewield any
# possible weapon, which requires a DB search.  Ugh, it doesn't feel right.  How about just the rewield function fails.  When
# the map is ready, WeaponBot gets set.
