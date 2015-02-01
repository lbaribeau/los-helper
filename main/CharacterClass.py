from misc_functions import *
from Ability import *
from ClassSkill import *
from CoolAbility import *

class CharacterClass(object):

    def __init__(self, class_string, telnetHandler, mudReaderHandler):
        self.id = class_string
        self.combat_skills = []
        self.heal_skills = []
        self.buff_skills = []

        if class_string == "Ass":
            self.lvl1_maxHP = 19 
            self.lvl1_maxMP = 2
            # self.abilities = [ Backstab(telnetHandler) ]
        elif class_string == "Bar":
            self.lvl1_maxHP = 24 
            self.lvl1_maxMP = 0
            self.mana_tick = 0
            self.mana_tick_chapel = 0
            # self.abilities = [ Bash(telnetHandler), Circle(telnetHandler), Berserk(telnetHandler) ]
        elif class_string == "Cle":
            self.lvl1_maxHP = 16 
            self.lvl1_maxMP = 4
            self.mana_tick = 2
            self.buff_skills.extend([ClassSkillReaction(mudReaderHandler, "Pray",
                                    SkillTimer("You feel extremely pious\.", 400),
                                    SkillTimer("Your prayers were not answered\.", 10),
                                   SkillTimer("You feel less pious\.", 285))])
            # self.abilities = [ Pray(telnetHandler), Turn(telnetHandler) ]
        elif class_string == "Fig":
            self.lvl1_maxHP = 22 
            self.lvl1_maxMP = 2
            # self.abilities = [ Bash(telnetHandler), Circle(telnetHandler) ]
        elif class_string == "Brd":
            self.lvl1_maxHP = 15 
            self.lvl1_maxMP = 3
            # self.abilities = [ AestersTears(telnetHandler), DanceOfTheCobra(telnetHandler) ]
        elif class_string == "Mag":
            self.lvl1_maxHP = 14 
            self.lvl1_maxMP = 5
            self.levelPath = [ ["out", "s", "w", "w", "w", "s", "e", "shop", "backroom", "portal"],
                          ["door", "out", "out", "w", "n", "e", "e", "e", "n", "cha"]]
        elif class_string == "Pal":
            self.lvl1_maxHP = 19 
            self.lvl1_maxMP = 3
            # self.abilities = [ Pray(telnetHandler), Turn(telnetHandler) ]
        elif class_string == "Ran":
            self.lvl1_maxHP = 18 
            self.lvl1_maxMP = 3
            self.HP_gained_per_level = 6
            self.MP_gained_per_level = 3
            self.mana_tick = 2 
            self.mana_tick_c#hapel = 4 
            # self.abilities = [ Haste(telnetHandler) ]
        elif class_string == "Thi":
            self.lvl1_maxHP = 18 
            self.lvl1_maxMP = 3
            # self.abilities = [ Backstab(telnetHandler), Steal(telnetHandler) ]
        elif class_string == "Mon":
            self.lvl1_maxHP = 17 
            self.lvl1_maxMP = 3
            self.HP_gained_per_level = 6
            self.MP_gained_per_level = 3
            self.heal_skills.extend([ClassSkillReaction(mudReaderHandler, "Meditate",
                                    SkillTimer("You feel at one with the universe\.", 105),
                                    SkillTimer("Your spirit is not at peace.", 10))])
            self.combat_skills.extend([ClassSkillReaction(mudReaderHandler, "Touch",
                                    SkillTimer("Your? touch(?:ed)? .+?\.", 240),
                                    SkillTimer("You failed to harm the .+?\.", 240))])
            # self.abilities = [ Meditate(telnetHandler), Touch(telnetHandler) ]
        elif class_string == "Dru":
            self.lvl1_maxHP = 15
            self.lvl1_maxMP = 4
            # self.abilities = [ Barkskin(telnetHandler) ]
        elif class_string == "Alc":
            self.lvl1_maxHP = 15 
            lvl1_maxMP = 4
        elif class_string == "Dar":
            lvl1_maxHP = 19 
            lvl1_maxMP = 4
            # abilities = [ Berserk(telnetHandler), Wither(telnetHandler) ]
        else:
            magentaprint("CharacterClass error: could not recognize class string.")

class ClassSkill(object):
    def command(self): 
        abstract()
    def cooldown_in_seconds_after_success(self): 
        abstract()
    def cooldown_in_seconds_after_failure(self):
        abstract()
    def use_for_combat(self):
        abstract()
    def success_mud_text(self):
        abstract()
    def failure_mud_text(self):
        abstract()
    def wear_off_mud_text(self):
        abstract()


# OLD IDEAS

# CombatAbility class?
#class CombatAbility:
#   ''' CombatAbilities are things that will affect how a character fights,
#    like circle, bash, steal, backstab, ''' 
#    def getCommand(self):
#        abstract()
#    def getCombatAlgorithm
# CombatAbility would be kind of like CoolAbility, but I can't imagine how 
# that approach would work for BotThread.  Instead use this CharacterClass 
# structure (canCircle, canBash, canSteal, etc.)


    # @property
    # def lvl1_maxHP(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def lvl1_maxMP(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def HP_gained_per_level(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def MP_gained_per_level(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def mana_tick_amount(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
 #   def abilities(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def level_path(self): raise NotImplementedError("Subclasses should implement this!")