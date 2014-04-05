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
    def command(self): 
        abstract()
    #TODO: Rename to getSuccessCooldown() and getFailureCooldown()
    def cooldown_in_seconds_after_success(self): 
        abstract()
    def cooldown_in_seconds_after_failure(self):
        abstract()
    def use_for_combat(self):
        ''' A boolean indicating whether the CoolAbility helps in combat.
        If false, assume it's useful in the chapel (ie. pray)''' 
        abstract()
    def needs_target(self):
        abstract()
    def needs_undead_target(self):
        abstract()
    def shares_cooldown_with_attack(self):
        abstract()
    def success_mud_text(self):
        abstract()
    def failure_mud_text(self):
        abstract()
    def wear_off_mud_text(self):
        abstract()
        
class Haste(CoolAbility):
    def command(self):
        return 'haste'
    def cooldown_in_seconds_after_success(self):
        return 600
    def cooldown_in_seconds_after_failure(self):
        return 10
    def use_for_combat(self):
        return True
    def needs_target(self):
        return False
    def needs_undead_target(self):
        return False
    def shares_cooldown_with_attack(self):
        return False
    def success_mud_text(self):
        return 'You feel yourself moving faster'
    def failure_mud_text(self):
        return 'Your attempt to hasten failed.'
    def wear_off_mud_text(self):
        return 'You feel slower.'
    
class Pray(CoolAbility):
    def command(self):
        return 'pray' 
    def cooldown_in_seconds_after_success(self):
        return 600
    def cooldown_in_seconds_after_failure(self):
        return 10
    def use_for_combat(self):
        return False
    def needs_target(self):
        return False
    def needs_undead_target(self):
        return False
    def shares_cooldown_with_attack(self):
        return False
    def success_mud_text(self):
        return 'You feel extremely pious.'
    def failure_mud_text(self):
        return 'Your prayers were not answered.'
    def wear_off_mud_text(self):
        return 'You feel less pious.'
    #Unneeded: You've already prayed.
    #Duration 5 minutes
    
class Barkskin(CoolAbility):
    def command(self):
        return 'barkskin' 
    def cooldown_in_seconds_after_success(self):
        return 600
    def cooldown_in_seconds_after_failure(self):
        return 10 #(?)
    def use_for_combat(self):
        return True
    def needs_target(self):
        return False
    def needs_undead_target(self):
        return False
    def shares_cooldown_with_attack(self):
        return False
    def success_mud_text(self):
        return 'You feel your skin thickening and hardening.'
    def failure_mud_text(self):
        return 'Your attempt to invoke barkskin failed.'
    def wear_off_mud_text(self):
        return 'Your skin softens.'
    #Unneeded: Your skin is already hardened.
    #Duration 2 minutes(?)
    #TODO: Does it conflict with steel bottle?
    
class Berserk(CoolAbility):
    #TODO: finish defining Berserk 
    def command(self):
        return 'berserk' 
    def cooldown_in_seconds_after_success(self):
        return abstract()  
    def cooldown_in_seconds_after_failure(self):
        return abstract()  
    def use_for_combat(self):
        return False
    def needs_target(self):
        return False
    def needs_undead_target(self):
        return False
    def shares_cooldown_with_attack(self):
        return False #not sure of this 
    def success_mud_text(self):
        return abstract() 
    def failure_mud_text(self):
        return abstract() 
    def wear_off_mud_text(self):
        return abstract()
    
class Meditate(CoolAbility):
    #TODO: finish defining Meditate 
    def command(self):
        return 'meditate' 
    def cooldown_in_seconds_after_success(self):
        return 125 #roughly 2 minutes
    def cooldown_in_seconds_after_failure(self):
        return 10 #guess
    def use_for_combat(self):
        return False
    def needs_target(self):
        return False
    def needs_undead_target(self):
        return False
    def shares_cooldown_with_attack(self):
        return False
    def success_mud_text(self):
        return "You feel at one with the universe."
    def failure_mud_text(self):
        return "Your spirit is not at peace."
    def wear_off_mud_text(self):
        return abstract()
    
class Wither(CoolAbility):
    #TODO: finish defining Wither
    def command(self): 
        return 'wither'
    def cooldown_in_seconds_after_success(self): 
        return 600 #guessed
    def cooldown_in_seconds_after_failure(self):
        return 30 #guessed
    def use_for_combat(self):
        return True
    def needs_target(self):
        return True
    def needs_undead_target(self):
        return False
    def shares_cooldown_with_attack(self):
        return True
    def success_mud_text(self):
        abstract()
    def failure_mud_text(self):
        abstract()
    def wear_off_mud_text(self):
        abstract()

class Touch:
    def command(self): 
        return 'touch'
    def cooldown_in_seconds_after_success(self): 
        return 600 #guessed
    def cooldown_in_seconds_after_failure(self):
        return 30 #guessed
    def use_for_combat(self):
        return True
    def needs_target(self):
        return True
    def needs_undead_target(self):
        return False
    def shares_cooldown_with_attack(self):
        return True
    def success_mud_text(self):
        abstract()
    def failure_mud_text(self):
        abstract()
    def wear_off_mud_text(self):
        abstract()

class Turn:
    def command(self): 
        return 'turn'
    def cooldown_in_seconds_after_success(self): 
        return 600 #guessed
    def cooldown_in_seconds_after_failure(self):
        return 30 #guessed
    def use_for_combat(self):
        return True
    def needs_target(self):
        return True
    def needs_undead_target(self):
        return True
    def shares_cooldown_with_attack(self):
        return True
    def success_mud_text(self):
        abstract()
    def failure_mud_text(self):
        abstract()
    def wear_off_mud_text(self):
        abstract()
