
from fake.fake_mobs.fake_mob import FakeMob
from fake.FakeItem import FakeItem

class Actor(FakeMob):
    def __init__(self, fake_character, socket):
        super().__init__(fake_character, socket)
        self.name = 'actor'  # This part could be automated, parsing the class name

    def sub_combat(self, rng):
        self.socket_output.append('[%s H %s M]: The %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
        if rng == 1:
            self.socket_output.append("Your iron ring fell apart.\n\r")
            ring = FakeItem('iron ring')
            ring.unusable = True
            self.char.inv.add(ring)
