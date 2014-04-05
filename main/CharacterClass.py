################################################################################

'''
Created on 2010-05-17

@author: laurier
'''

# Abstract class...
# source http://norvig.com/python-iaq.html

def abstract():
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')


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

class CharacterClass:
    ''' These are objects to store data about the character classes.'''
    def getLevelOneMaxHealth(self): abstract()
    def getLevelOneMaxMana(self): abstract()
    def getHealthGainedPerLevel(self): abstract()
    def getManaGainedPerLevel(self): abstract()
    def getCanCircle(self): abstract()
    def getCanBash(self): abstract()
    def getCanSteal(self): abstract() 
    def getCanBackstab(self): abstract() 
    def getCoolAbilities(self): abstract()
    def getLevelPath(self): return [ ]
 
class Ranger(CharacterClass):   
    def getLevelOneMaxHealth(self): return 18
    def getLevelOneMaxMana(self): return 3
    def getHealthGainedPerLevel(self): return 6
    def getManaGainedPerLevel(self): return 3
    def getManaTickAmount(self): return 2
    def getCanCircle(self): return False
    def getCanBash(self): return False
    def getCanSteal(self): return False
    def getCanBackstab(self): return False
    def getCoolAbilities(self): return [ Haste() ]
    def getLevelPath(self): return [ ]

class Monk(CharacterClass):   
    def getLevelOneMaxHealth(self): return 17
    def getLevelOneMaxMana(self): return 3
    def getHealthGainedPerLevel(self): return 6
    def getManaGainedPerLevel(self): return 3
    def getManaTickAmount(self): return 2
    def getCanCircle(self): return False
    def getCanBash(self): return False
    def getCanSteal(self): return False
    def getCanBackstab(self): return False
    def getCoolAbilities(self): return [ Meditate(), Touch() ]
    def getLevelPath(self): return [ ]

class Mage(CharacterClass):
    def getLevelOneMaxHealth(self): return 17
    def getLevelOneMaxMana(self): return 3
    def getHealthGainedPerLevel(self): return 6
    def getManaGainedPerLevel(self): return 3
    def getManaTickAmount(self): return 2
    def getCanCircle(self): return False
    def getCanBash(self): return False
    def getCanSteal(self): return False
    def getCanBackstab(self): return False
    def getCoolAbilities(self): return [ ]
    def getLevelPath(self): return [ ["out", "s", "w", "w", "w", "s", "e", "shop", "backroom", "portal"],["door", "out", "out", "w", "n", "e", "e", "e", "n", "cha"]]

#class Paladin(CharacterClass):   
    #def getLevelOneMaxHealth(self): return 17
    #def getLevelOneMaxMana(self): return 3
    #def getHealthGainedPerLevel(self): return 6
    #def getManaGainedPerLevel(self): return 3
    #def getManaTickAmount(self): return 2
    #def getCanCircle(self): return False
    #def getCanBash(self): return False
    #def getCanSteal(self): return False
    #def getCanBackstab(self): return False
    #def getCoolAbilities(self): return [ Pray(), Turn() ]
    
#class Druid(CharacterClass):   
    #def getLevelOneMaxHealth(self): return 15
    #def getLevelOneMaxMana(self): return 4
    #def getHealthGainedPerLevel(self): return 6
    #def getManaGainedPerLevel(self): return 3
    #def getManaTickAmount(self): return 2
    #def getCanCircle(self): return False
    #def getCanBash(self): return False
    #def getCanSteal(self): return False
    #def getCanBackstab(self): return False
    #def getCoolAbilities(self): return [ Barkskin() ]

