
from Ability import *

class CharacterClass(object):

    def __init__(self, class_string, mudReaderHandler, telnetHandler):
        self.id = class_string

        if class_string == "Ass":
            self.lvl1_maxHP = 19 
            self.lvl1_maxMP = 2
            self.abilities = [ Backstab(mudReaderHandler, telnetHandler) ]
        elif class_string == "Bar":
            self.lvl1_maxHP = 24 
            self.lvl1_maxMP = 0
            self.mana_tick = 0
            self.mana_tick_chapel = 0
            self.abilities = [ Bash(mudReaderHandler, telnetHandler), Circle(mudReaderHandler, telnetHandler), Berserk(mudReaderHandler, telnetHandler) ]
        elif class_string == "Cle":
            self.lvl1_maxHP = 16 
            self.lvl1_maxMP = 4
            self.mana_tick = 2
            self.abilities = [ Pray(mudReaderHandler, telnetHandler), Turn(mudReaderHandler, telnetHandler) ]
        elif class_string == "Fig":
            self.lvl1_maxHP = 22 
            self.lvl1_maxMP = 2
            self.abilities = [ Bash(mudReaderHandler, telnetHandler), Circle(mudReaderHandler, telnetHandler) ]
        elif class_string == "Brd":
            self.lvl1_maxHP = 15 
            self.lvl1_maxMP = 3
            self.abilities = [ AestersTears(mudReaderHandler, telnetHandler), DanceOfTheCobra(mudReaderHandler, telnetHandler) ]
        elif class_string == "Mag":
            self.lvl1_maxHP = 14 
            self.lvl1_maxMP = 5
            self.levelPath = [ ["out", "s", "w", "w", "w", "s", "e", "shop", "backroom", "portal"],
                          ["door", "out", "out", "w", "n", "e", "e", "e", "n", "cha"]]
        elif class_string == "Pal":
            self.lvl1_maxHP = 19 
            self.lvl1_maxMP = 3
            self.abilities = [ Pray(mudReaderHandler, telnetHandler), Turn(mudReaderHandler, telnetHandler) ]
        elif class_string == "Ran":
            self.lvl1_maxHP = 18 
            self.lvl1_maxMP = 3
            self.HP_gained_per_level = 6
            self.MP_gained_per_level = 3
            self.mana_tick = 2 
            self.mana_tick_chapel = 4 
            self.abilities = [ Haste(mudReaderHandler, telnetHandler) ]
        elif class_string == "Thi":
            self.lvl1_maxHP = 18 
            self.lvl1_maxMP = 3
            self.abilities = [ Backstab(mudReaderHandler, telnetHandler), Steal(mudReaderHandler, telnetHandler) ]
        elif class_string == "Mon":
            self.lvl1_maxHP = 17 
            self.lvl1_maxMP = 3
            self.HP_gained_per_level = 6
            self.MP_gained_per_level = 3
            self.abilities = [ Meditate(mudReaderHandler, telnetHandler), Touch(mudReaderHandler, telnetHandler) ]
        elif class_string == "Dru":
            self.lvl1_maxHP = 15
            self.lvl1_maxMP = 4
            self.abilities = [ Barkskin(mudReaderHandler, telnetHandler) ]
        elif class_string == "Alc":
            self.lvl1_maxHP = 15 
            lvl1_maxMP = 4
        elif class_string == "Dar":
            lvl1_maxHP = 19 
            lvl1_maxMP = 4
            abilities = [ Berserk(mudReaderHandler, telnetHandler), Wither(mudReaderHandler, telnetHandler) ]
        else:
            magentaprint("CharacterClass error: could not recognize class string.")





# OLD IDEAS

# CombatAbility class?
#class CombatAbility:
#    ''' CombatAbilities are things that will affect how a character fights,
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
    # def abilities(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def level_path(self): raise NotImplementedError("Subclasses should implement this!")