
from fake.fake_mobs.fake_mob import FakeMob

class Bruiser(FakeMob):
    def __init__(self, fake_character, socket):
        super().__init__(fake_character, socket)
        self.name = 'bruiser'  # This part could be automated, parsing the class name

    def sub_combat(self, rng):
        self.socket_output.append('[%s H %s M]: The bruiser throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp)))
        if rng == 3:
            self.socket_output.append("Your iron ring fell apart.\n\r")
