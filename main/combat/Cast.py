
import re
from time import time

from combat.CombatObject import SimpleCombatObject
from comm import RegexStore
from misc_functions import magentaprint
from comm import Spells
from Aura import Aura

class Cast(SimpleCombatObject):
    command = 'c v'  # This gets rewritten to append the spellname alot
    cooldown_after_success = 4  # Gets rewritten by characterClass...
    cooldown_after_failure = 0
    regexes = []
    aura = None
    # cast = RegexStore.cast
    success_regexes = [RegexStore.cast, RegexStore.bind_cast, RegexStore.confusion_cast, RegexStore.aura, RegexStore.mob_aura]
    failure_regexes = [RegexStore.cast_failure, RegexStore.no_mana]
    error_regexes = [RegexStore.bad_target_or_spell, RegexStore.not_here, RegexStore.use_what]

    vig_amount = 2
    mend_amount = 5
    # showaura_amount = 1
    # light_amount = 5
    # lvl1_black_amount = 3
    # lvl2_black_amount = 7
    # prot_amount = 10

    def __init__(self, telnetHandler, use):
        super().__init__(telnetHandler)

        self.use = use
        self.end_combat_regexes.append(RegexStore.no_mana)
        self.regex_cart.append(RegexStore.hit_with_confusion)

    # Commented... hmmm.. I went with the notify_failure(), I think so I wasn't checking for the regex twice...
    # Just a logic structure thing.
       # def notify(self, regex, M_obj):
       #     if regex is self.spell_failed:
       #         # Looks like we need spell to be instance or class variable
       #         # What is it currently - it's currently part of command I believe...
       #         # does this code even work yet.... command will just get changed...
       #         # ... so we can get spell from command here inevitably...
       #         if re.match("vig?|vigor?", spell):
       #             self.__class__.timer = self.__class__.timer - self.cooldown_after_success + self.cooldown_after_failure
       #         pass
       #     super().notify(regex, M_obj)

    def notify(self, regex, M_obj):
        if regex in RegexStore.cast:
            # magentaprint("cast notified: " + str(M_obj.group(0)), False)
            if "over" in M_obj.groupdict() and M_obj.group('over') is not None:
                # magentaprint("Mob killed - stopping cast thread", False)
                self.target_dead = True
                self.stop()
        elif regex in RegexStore.hit_with_confusion:
            magentaprint("I'ma confused oh my!!", False)
            self.start_timer() # restart the timer
        elif regex in RegexStore.aura:
            self.aura = Aura(M_obj.group('aura'))
        elif regex in RegexStore.no_mana:
            self.stop()
        super().notify(regex, M_obj)

        # TODO: Having a red aura in the chapel will kill the bot.
        #M_obj = re.search("The goodness here sickens and repels you!", text_buffer)
        #if(M_obj):
        #    text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
        ##    self.CommandHandler_inst.process("ou")

    def notify_failure(self, regex, M_obj):
        # spell = self.command.split(' ')[1].lower() if len(self.command.split(' ')) > 0 else ""
        # 'read paper' 'Your spell fails' causes index error, re.search works around it
        # if re.search("vi?|vigo?|vigor", self.command) or \
        #    re.search("show-?|show-au?|show-aura?", self.command) or \
        #    re.search("lig?|light?", self.command) or \
        #    re.search("me?|mend?|mend-w?|mend-wou?|mend-wound?|mend-wounds", self.command):
        # if self.command.split(' ')[1].startswith(Spells.vigor) or \
        #    self.command.split(' ')[1].startswith(Spells.showaura) or \
        #    self.command.split(' ')[1].startswith(Spells.light) or \
        #    self.command.split(' ')[1].startswith(Spells.mendwounds):
        # if any(self.command.split(' ')[1].startswith(s) for s in Spells.vigor, Spells.showaura, Spells.light, Spells.mendwounds):
        if any(self.command.split(' ')[1].startswith(s) for s in (Spells.vigor, Spells.showaura, Spells.light, Spells.mendwounds)):
            magentaprint("Cast notify failure clearing timer.")
            self.clear_timer()
        # TODO: Erhm I think this can be done smarter - the parent doesn't need to be involved.

    def set_spell(self, spell, is_item=False):
        magentaprint("Cast setting command to \'" + 'c ' + str(spell) + "\'")
        if not is_item:
            self.command = 'c ' + spell
        else:
            self.command = 'use ' + spell

    def start_thread(self, spell, target=None):
        # self.command = 'c ' + spell
        self.set_spell(spell)
        super().start_thread(target)

    def cast(self, spell, target=None):
        # self.command = 'c ' + spell
        self.set_spell(spell)
        self.execute(target)
        # self.wait_for_flag()
        # I think I only need to provide waiting calls since other 
        # calls can just be done with telnetHandler
        # Maybe the way to go is @classmethods need not wait (human use,)
        # and calls using the instance will wait.
        # The caller even has access to wait_for_flag so this is not important.

        # Keep in mind that cls.target is for thread use.

    def persistent_cast(self, spell, target=None, is_item=False):
        # This just spams on Please wait, and spam_spell also deals with Spell failed.
        # self.__class__.command = 'c ' + spell
        self.set_spell(spell, is_item)
        self.persistent_execute(target)

    def update_aura(self, character, use_item=""):
        magentaprint("Cast.update_aura()")
        # magentaprint("{} {} {}".format(time(), self.aura_timer + self.aura_refresh, time() > (self.aura_timer + self.aura_refresh)),False)
        self.stopping = False
        if not use_item:
            if Spells.showaura not in character.spells:
                magentaprint("Cast giving up on aura update.")
                return
 
            self.spam_spell(character, Spells.showaura)
            character.AURA = str(self.aura)
        else:
            self.use.execute_and_wait(use_item)
            character.AURA = str(self.use.aura)

    def spam_spell(self, character, spell, target=None):  # Maybe a prompt object would be better than character
        # Spam until success
        # if spell not in character.spells:
        if not any(spell.startswith(s) for s in character.spells):
            magentaprint("Cast.spam_spell aborted - %s not in %s." % (str(spell), str(character.spells)), False)
            return

        spell_cost = self.vig_amount if spell.startswith(Spells.vigor) else \
                     1 if spell.startswith(Spells.showaura) else \
                     5 if spell.startswith(Spells.light) else \
                     10 if spell.startswith(Spells.protection) else \
                     self.mend_amount if spell.startswith(Spells.mendwounds) else 3

        self.result = RegexStore.cast_failure[0]

        while self.failure and character.MANA >= spell_cost and not self.stopping:
            # magentaprint("Cast object spamming! Woo!")
            self.wait_until_ready()
            self.cast(spell, target)
            self.wait_for_flag()
