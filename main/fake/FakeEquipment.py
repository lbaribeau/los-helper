
class FakeEquipment(object):
    def __init__(self, character_name):
        self.character_name = character_name
        self.weapon = ''
        self.seconded = ''

    def lself(self):
        return "You see " + self.character_name + " the Human Vicar.\n" "He is in general good health.\n" + self.output_string()

    def output_string(self):
        armour = (
            "On body:   some chain mail armour\n"
            "On arms:   some chain mail sleeves\n"
            "On legs:   some chain mail leggings\n"
            "On neck:   a grey cloak\n"
            "On neck:   a traveller's cross\n"
            "On hands:  some chain mail gloves\n"
            "On head:   a chain mail hood\n"
            "On feet:   some chain mail boots\n"
            "On face:   some spectacles\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "Shield:    a cast iron shield\n"
        )
        if self.weapon:
            armour += "Wielded:   " + self.weapon + '\n'
        else:
            return armour
            
        if self.seconded:
            return armour + "Seconded:  " + self.seconded + "\n"
        else:
            return armour

    def wield(self, weapon):
        self.weapon = weapon

    def second(self, weapon):
        self.seconded = weapon


