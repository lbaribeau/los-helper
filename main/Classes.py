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
    ''' CoolAbilites are things like haste, pray, barkskin, meditate, berserk,
    wither, touch, turn'''    
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
        return abstract()  
    def getCoolDownInSecondsAfterFail(self):
        return abstract()  
    def getUseForCombat(self):
        return False
    def getNeedsTarget(self):
        return False
    def getMudTextThatMeansSuccess(self):
        return abstract() 
    def getMudTextThatMeansFailure(self):
        return abstract() 
    def getMudTextThatMeansItWoreOff(self):
        return abstract()

class CharacterClass:
    ''' These are objects to store data about the character classes.'''
    def getHealthTickAmountInChapel(self): abstract()
    def getManaTickAmountInChapel(self): abstract()
    def getLevelOneMaxHealth(self): abstract()
    def getLevelOneMaxMana(self): abstract()
    def getHealthGainedPerLevel(self): abstract()
    def getManaGainedPerLevel(self): abstract()
    def getCanCircle(self): abstract()
    def getCanBash(self): abstract()
    def getCanBackstab(self): abstract() 
    def getCanSteal(self): abstract() 
    #TODO: should this be a CoolAbility?
    #Or should it be worked into the combat
    #algorithm?
    def getCoolAbilities(self): abstract()
    def getUseCoolAbilityForCombat(self): abstract()
    


    
    
    

