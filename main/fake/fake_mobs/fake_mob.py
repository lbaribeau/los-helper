
class FakeMob(object):
    def __init__(self, fake_character, socket_output_array):
        self.char = fake_character
        self.socket_output = socket_output_array
        self.rng = 0

    def do_combat(self):
        self.rng = (self.rng + 1) % 4
        if self.rng == 0:
            self.socket_output.append('Your attack overwhelms the ' + self.name + ' and he collapses!\nYour enemy, the ' + self.name + ' has been defeated.\nYou gain 11 experience.\n')
            return True
        else:
            self.sub_combat(self.rng)
