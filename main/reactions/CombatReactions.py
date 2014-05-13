from BotReactions import *
from misc_functions import *
from Database import *
from MudMap import *

class CombatReactions(BotReaction):
    def __init__(self, mudReaderHandler, character):
        #self.physical_hit_type = "You (head-butt|kick|grab|lash out( at| and thump)?) the (.+?)( and gouge him)?"

        self.physical_damage = "You (.+?) the (.+?) for ([\d]*) damage\."
        self.physical_miss = "You (.+?) the (.+?), but (.+?)\." #keyword "but" means ignore everything - you missed
        self.physical_critical = "(The|Your?).+?!!"

        #self.mob_physical_hit_type = " (kicks|punches|lashes out|throws a wild punch at) you"        
        self.mob_physical_damage = "The (.+?) ([\d]) damage\." 
        self.mob_physical_miss = "The (.+?) you, but (.+?)\."

        self.spell_type = "You cast a (.+?) spell on (.+?)\."
        self.spell_damage_dealt = "The spell did ([\d]*) damage\."
        self.spell_fails = "Your spells fails\."

        self.regexes = [self.physical_damage,
                        self.physical_miss,
                        self.physical_critical,
                        self.mob_physical_damage,
                        self.mob_physical_miss,
                        self.spell_damage_dealt,
                        self.spell_fails]

        self.mudReaderHandler = mudReaderHandler
        self.character = character

        self.good_MUD_timeout = 1.5
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        magentaprint("Combat Reaction happened on: " + regex)
        if regex == self.physical_damage:
            self.character.HITS_DEALT += 1

            damage_dealt = int(M_obj.group(3))
            self.character.DAMAGE_DEALT += damage_dealt

            if (self.character.HIGHEST_DAMAGE < damage_dealt):
                self.character.HIGHEST_DAMAGE = damage_dealt
            if (self.character.LOWEST_DAMAGE > damage_dealt):
                self.character.LOWEST_DAMAGE = damage_dealt

        elif regex == self.physical_miss:
            self.character.HITS_MISSED += 1

        elif regex == self.physical_critical:
            self.character.CRITS_LANDED += 1

        elif regex == self.mob_physical_damage:
            self.character.HITS_RECEIVED += 1
            damage_taken = int(M_obj.group(2))
            self.character.DAMAGE_TAKEN += damage_taken

        elif regex == self.mob_physical_miss:
            self.character.HITS_EVADED += 1

        elif regex == self.spell_damage_dealt:
            self.character.SPELLS_CAST += 1
            damage_dealt = int(M_obj.group(1))
            self.character.SPELL_DAMAGE_DEALT += damage_dealt

            if (self.character.HIGHEST_DAMAGE < damage_dealt):
                self.character.HIGHEST_DAMAGE = damage_dealt
            if (self.character.LOWEST_DAMAGE > damage_dealt):
                self.character.LOWEST_DAMAGE = damage_dealt

        elif regex == self.spell_fails:
            self.character.SPELLS_CAST += 1
            self.character.SPELLS_FAILED += 1
