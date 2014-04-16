
from Ability import *

class CharacterClass(object):
    ''' These are objects to store data about the character classes.'''
    @property
    def lvl1_maxHP(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def lvl1_maxMP(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def HP_gained_per_level(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def MP_gained_per_level(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def mana_tick_amount(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def can_circle(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def can_bash(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def can_steal(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def can_backstab(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def abilities(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def level_path(self): raise NotImplementedError("Subclasses should implement this!")

dummyTelnet = 1

class Ranger(CharacterClass):   
    lvl1_maxHP = 18 
    lvl1_maxMP = 3
    HP_gained_per_level = 6
    MP_gained_per_level = 3
    mana_tick_amount = 2 
    can_circle = False
    can_bash = False
    can_steal = False
    can_backstab = False
    abilities = [ Haste(dummyTelnet) ]
    # level_path

class Monk(CharacterClass):   
    lvl1_maxHP = 17 
    lvl1_maxMP = 3
    HP_gained_per_level = 6
    MP_gained_per_level = 3
    mana_tick_amount = 2 
    can_circle = False
    can_bash = False
    can_steal = False
    can_backstab = False
    abilities = [ Meditate(dummyTelnet), Touch(dummyTelnet) ]
    # level_path

class Mage(CharacterClass):
    # Todo: fill in correct numbers
    lvl1_maxHP = 17 
    lvl1_maxMP = 3
    HP_gained_per_level = 6
    MP_gained_per_level = 3
    mana_tick_amount = 2 
    can_circle = False
    can_bash = False
    can_steal = False
    can_backstab = False
    abilities = [ Meditate(dummyTelnet), Touch(dummyTelnet) ]
    levelPath = [ ["out", "s", "w", "w", "w", "s", "e", "shop", "backroom", "portal"],
                  ["door", "out", "out", "w", "n", "e", "e", "e", "n", "cha"]]

#class Paladin(CharacterClass):   
    #lvl1_maxHP = 17
    #lvl1_maxMP = 3
    #abilities = [ Pray(), Turn() ]
    
#class Druid(CharacterClass):   
    #lvl1_maxHP = 15
    #lvl1_maxMP = 4
    #abilities  = [ Barkskin() ]


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

