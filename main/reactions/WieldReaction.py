
from misc_functions import magentaprint

class WieldReaction(object):
    """ notify will execute wield commands."""
    
    def __init__(self, character, telnetHandler):
        # Note: regex should specify the weapon string in a group.
        self.regexes = [ "Your (.+?) breaks and you have to remove it\.",
                         "Your (.+?) shatters\."]
        self.character = character
        self.telnetHandler = telnetHandler

    def notify(self, regex, M_obj):
        magentaprint("Reequiping weapon..." + M_obj.group(1))
        self.reequip_weapon(M_obj.group(1))
        
    def reequip_weapon(self, weapon):        
        if self.character.weapon1 == self.character.weapon2:
            self.telnetHandler.write("wie " + weapon)
            self.telnetHandler.write("seco " + weapon)
        else:
            if self.character.inventory.has(weapon):
                if weapon == self.character.weapon1:
                    self.telnetHandler.write("wie " + self.character.inventory.get_2nd_word_reference(weapon))
                else:
                    self.telnetHandler.write("seco " + self.character.inventory.get_2nd_word_reference(weapon))
