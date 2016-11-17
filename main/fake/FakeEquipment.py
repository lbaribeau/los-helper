
class FakeEquipment(object):
    def __init__(self, character_name):
        self.character_name = character_name
        self.weapon = ''
        self.seconded = ''

    def lself(self):
        return "You see " + self.character_name + " the Human Vicar.\n\r" "He is in general good health.\n\r" + self.output_string()

    def output_string(self):
        armour = (
            "On body:   some chain mail armour\n\r"
            "On arms:   some chain mail sleeves\n\r"
            "On legs:   some chain mail leggings\n\r"
            "On neck:   a grey cloak\n\r"
            "On neck:   a traveller's cross\n\r"
            "On hands:  some chain mail gloves\n\r"
            "On head:   a chain mail hood\n\r"
            "On feet:   some chain mail boots\n\r"
            "On face:   some spectacles\n\r"
            "On finger: an iron ring\n\r"
            "On finger: an iron ring\n\r"
            "On finger: an iron ring\n\r"
            "On finger: an iron ring\n\r"
            "On finger: an iron ring\n\r"
            "On finger: an iron ring\n\r"
            "On finger: an iron ring\n\r"
            "On finger: an iron ring\n\r"
            "Shield:    a cast iron shield\n\r"
        )
        if self.weapon:
            armour += "Wielded:   " + self.weapon + "\n\r"
        else:
            return armour

        if self.seconded:
            return armour + "Seconded:  " + self.seconded + "\n\r"
        else:
            return armour

    def wield(self, weapon):
        self.weapon = weapon

    def second(self, weapon):
        self.seconded = weapon


