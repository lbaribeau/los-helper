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

class CoolAbility:
    ''' CoolAbilites are things like haste, barkskin, berserk, meditate, pray,
    wither, touch, turn.  Things that drastically affect combat such as 
    circle, bash, backstab, steal, are NOT CoolAbilities.  They are worked 
    into the CharacterClass a little differently.'''    
    def getCommand(self): 
        abstract()
    def getCooldownInSecondsAfterSuccess(self): 
        abstract()
    def getCooldownInSecondsAfterFail(self):
        abstract()
    def getUseForCombat(self):
        ''' A boolean indicating whether the CoolAbility helps in combat.
        If false, assume it's useful in the chapel (ie. pray)''' 
        abstract()
    def getNeedsTarget(self):
        abstract()
    def getNeedsUndeadTarget(self):
        abstract()
    def getSharesCooldownWithAttack(self):
        abstract()
    def getMudTextThatMeansSuccess(self):
        abstract()
    def getMudTextThatMeansFailure(self):
        abstract()
    def getMudTextThatMeansItWoreOff(self):
        abstract()
        
class Haste(CoolAbility):
    def getCommand(self):
        return 'haste'
    def getCoolDownInSecondsAfterSuccess(self):
        return 600
    def getCoolDownInSecondsAfterFail(self):
        return 10
    def getUseForCombat(self):
        return True
    def getNeedsTarget(self):
        return False
    def getNeedsUndeadTarget(self):
        return False
    def getSharesCooldownWithAttack(self):
        return False
    def getMudTextThatMeansSuccess(self):
        return 'You feel yourself moving faster'
    def getMudTextThatMeansFailure(self):
        return 'Your attempt to hasten failed.'
    def getMudTextThatMeansItWoreOff(self):
        return 'You feel slower.'
    
class Pray(CoolAbility):
    #TODO: finish defining Pray (cooldowns, mud text)
    def getCommand(self):
        return 'pray' 
    def getCoolDownInSecondsAfterSuccess(self):
        return abstract()  
    def getCoolDownInSecondsAfterFail(self):
        return abstract()  
    def getUseForCombat(self):
        return False
    def getNeedsTarget(self):
        return False
    def getNeedsUndeadTarget(self):
        return False
    def getSharesCooldownWithAttack(self):
        return False
    def getMudTextThatMeansSuccess(self):
        return abstract() 
    def getMudTextThatMeansFailure(self):
        return abstract() 
    def getMudTextThatMeansItWoreOff(self):
        return abstract()
    
class Barkskin(CoolAbility):
    #TODO: finish defining Barkskin 
    def getCommand(self):
        return 'barkskin' 
    def getCoolDownInSecondsAfterSuccess(self):
        return abstract()  
    def getCoolDownInSecondsAfterFail(self):
        return abstract()  
    def getUseForCombat(self):
        return True
    def getNeedsTarget(self):
        return False
    def getNeedsUndeadTarget(self):
        return False
    def getSharesCooldownWithAttack(self):
        return False
    def getMudTextThatMeansSuccess(self):
        return abstract() 
    def getMudTextThatMeansFailure(self):
        return abstract() 
    def getMudTextThatMeansItWoreOff(self):
        return abstract()
    
class Berserk(CoolAbility):
    #TODO: finish defining Berserk 
    def getCommand(self):
        return 'berserk' 
    def getCoolDownInSecondsAfterSuccess(self):
        return abstract()  
    def getCoolDownInSecondsAfterFail(self):
        return abstract()  
    def getUseForCombat(self):
        return False
    def getNeedsTarget(self):
        return False
    def getNeedsUndeadTarget(self):
        return False
    def getSharesCooldownWithAttack(self):
        return False #not sure of this 
    def getMudTextThatMeansSuccess(self):
        return abstract() 
    def getMudTextThatMeansFailure(self):
        return abstract() 
    def getMudTextThatMeansItWoreOff(self):
        return abstract()
    
class Meditate(CoolAbility):
    #TODO: finish defining Meditate 
    def getCommand(self):
        return 'meditate' 
    def getCoolDownInSecondsAfterSuccess(self):
        return 600 #guess
    def getCoolDownInSecondsAfterFail(self):
        return 10 #guess
    def getUseForCombat(self):
        return False
    def getNeedsTarget(self):
        return False
    def getNeedsUndeadTarget(self):
        return False
    def getSharesCooldownWithAttack(self):
        return False
    def getMudTextThatMeansSuccess(self):
        return abstract() 
    def getMudTextThatMeansFailure(self):
        return abstract() 
    def getMudTextThatMeansItWoreOff(self):
        return abstract()
    
class Wither(CoolAbility):
    #TODO: finish defining Wither
    def getCommand(self): 
        return 'wither'
    def getCooldownInSecondsAfterSuccess(self): 
        return 600 #guessed
    def getCooldownInSecondsAfterFail(self):
        return 30 #guessed
    def getUseForCombat(self):
        return True
    def getNeedsTarget(self):
        return True
    def getNeedsUndeadTarget(self):
        return False
    def getSharesCooldownWithAttack(self):
        return True
    def getMudTextThatMeansSuccess(self):
        abstract()
    def getMudTextThatMeansFailure(self):
        abstract()
    def getMudTextThatMeansItWoreOff(self):
        abstract()

class Touch:
    def getCommand(self): 
        return 'touch'
    def getCooldownInSecondsAfterSuccess(self): 
        return 600 #guessed
    def getCooldownInSecondsAfterFail(self):
        return 30 #guessed
    def getUseForCombat(self):
        return True
    def getNeedsTarget(self):
        return True
    def getNeedsUndeadTarget(self):
        return False
    def getSharesCooldownWithAttack(self):
        return True
    def getMudTextThatMeansSuccess(self):
        abstract()
    def getMudTextThatMeansFailure(self):
        abstract()
    def getMudTextThatMeansItWoreOff(self):
        abstract()

class Turn:
    def getCommand(self): 
        return 'turn'
    def getCooldownInSecondsAfterSuccess(self): 
        return 600 #guessed
    def getCooldownInSecondsAfterFail(self):
        return 30 #guessed
    def getUseForCombat(self):
        return True
    def getNeedsTarget(self):
        return True
    def getNeedsUndeadTarget(self):
        return True
    def getSharesCooldownWithAttack(self):
        return True
    def getMudTextThatMeansSuccess(self):
        abstract()
    def getMudTextThatMeansFailure(self):
        abstract()
    def getMudTextThatMeansItWoreOff(self):
        abstract()

# Commented because I don't see how this approach (using CombatAbility 
# classes,) would work.
# I think the CharacterClass should have canCircle, canBash, canSteal, 
# and canBackstab, and the bot thread will define the combat algorithm 
# based on those values.
#class CombatAbility:
#    ''' CombatAbilities are things that will affect how a character fights,
#    like circle, bash, steal, backstab, ''' 
#    def getCommand(self):
#        abstract()
#    def getCombatAlgorithm

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
    def getCoolAbilities(self): return [ Meditate(), Touch() ]

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
    def getCoolAbilities(self): return [ Haste() ]
    
    
    

