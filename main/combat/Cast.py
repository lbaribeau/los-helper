
import re
from time import time

from combat.CombatObject import SimpleCombatObject
from comm import RegexStore
from command import Spells
from misc_functions import magentaprint

class Cast(SimpleCombatObject):
    command = 'c'  # This gets rewritten to append the spellname alot
    cooldown_after_success = 4  # Gets rewritten by characterClass...
    cooldown_after_failure = 0
    regexes = []  

    success_regexes = [RegexStore.cast, RegexStore.aura]
    failure_regexes = [RegexStore.cast_failure, RegexStore.no_mana]
    error_regexes = [RegexStore.bad_target_or_spell, RegexStore.not_here]

    aura = None
    aura_timer = 0
    aura_refresh = 480

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)
        self.end_combat_regexes.append(RegexStore.no_mana)

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
        if regex in RegexStore.aura:
            self.__class__.aura = M_obj.group(1)
            self.__class__.aura_timer = time()
        elif regex in RegexStore.no_mana:
            self.stop()
        super().notify(regex, M_obj)

    def notify_failure(self, regex, M_obj):
        # spell = self.command.split(' ')[1].lower() if len(self.command.split(' ')) > 0 else ""
        # 'read paper' 'Your spell fails' causes index error, re.search works around it
        if re.search("vi?|vigo?|vigor", self.command) or \
           re.search("show-?|show-au?|show-aura?", self.command) or \
           re.search("lig?|light?", self.command) or \
           re.search("me?|mend?|mend-w?|mend-wou?|mend-wound?|mend-wounds", self.command):
            magentaprint("Cast notify failure clearing timer.")
            self.clear_timer()
        # TODO: Erhm I think this can be done smarter - the parent doesn't need to be involved.

    def set_spell(self, spell):
        magentaprint("Cast setting command to \'" + 'c ' + str(spell) + "\'")
        self.__class__.command = 'c ' + spell

    def start_thread(self, spell, target=None):
        # self.__class__.command = 'c ' + spell
        self.set_spell(spell)
        super().start_thread(target)

    def cast(self, spell, target=None):
        # self.__class__.command = 'c ' + spell
        self.set_spell(spell)
        self.execute(target)
        # self.wait_for_flag()
        # I think I only need to provide waiting calls since other 
        # calls can just be done with telnetHandler
        # Maybe the way to go is @classmethods need not wait (human use,)
        # and calls using the instance will wait.
        # The caller even has access to wait_for_flag so this is not important.

        # Keep in mind that cls.target is for thread use.

    def persistent_cast(self, spell, target=None):
        # This just spams on Please wait, and spam_spell also deals with Spell failed.
        # self.__class__.command = 'c ' + spell
        self.set_spell(spell)
        self.persistent_execute(target)

    def update_aura(self, character):
        if not 'show-aura' in character.spells:
            return

        if time() > self.aura_timer + self.aura_refresh:
            self.spam_spell(character, Spells.showaura)
            # self.cast('show')
            # self.wait_for_flag()
            # while self.result is 'failure':
            #     self.cast('show')
            #     self.wait_for_flag()
            # if self.success:
            #     self.aura_timer = time.time()
        #else:
            #magentaprint("Last aura update %d seconds ago." % round(time.time() - self.aura_timer))

    def spam_spell(self, character, spell, target=None):  # Maybe a prompt object would be better than character
        # Spam until success
        if spell not in character.spells:
            return

        spell_cost = 2 if re.match("vig?|vigor?", spell) else \
                     1 if re.match("show?|show-a?|show-aura?", spell) else \
                     5 if re.match("lig?|light?", spell) else 3

        self.result = RegexStore.cast_failure[0]

        while self.failure and character.MANA >= spell_cost and not self.stopping:
            self.wait_until_ready()
            self.cast(spell, target)
            self.wait_for_flag()

