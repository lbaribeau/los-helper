
from fake.fake_command import FakeCommand
from misc_functions import magentaprint

class FakeUse(FakeCommand):
    def __init__(self, character, socket_output):
        super().__init__(socket_output)
        self.char = character
        self.inv = character.inv
        self.pots = [
            "small restorative", "large restorative", "chicken soup", "scarlet potion", "small flask",
            "white potion", "steel bottle", "silver chalice", "milky potion"
        ]
        self.large_pots = ["large restorative", "scarlet potion"]

    def do(self, target):
        i = self.inv.index(target)
        magentaprint("FakeUse.do i " + str(i))
        
        if i is None:
            self.socket_output.append("Use what?\n\r")
        elif self.inv.l[i].to_string() not in self.pots:
            self.socket_output.append("How does one use that?\n\r")
        else:
            if self.inv.l[i].to_string() in self.large_pots:
                self.char.hp = self.char.hp + 20
            else:
                self.char.hp = self.char.hp + 4
            self.socket_output.append('Potion drank.\n\rYou feel much better.\n\rA %s disintegrates.\n\r' % self.inv.l[i].to_string())
            self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))
            self.inv.remove_by_index(i)

        # todo maybe: flask doesn't get consumed immediately
        # if 'small flask' in self.pots:
        #     self.flask_rng = self.flask_rng + 1 % 2
        #     self.char.hp = self.char.hp + 2
        #     if self.flask_rng == 1:
        #         self.socket_output.append('Potion drank.\n\rYou feel much better.\n\r')
        #     else:
        #         self.pots.remove('small flask')
        #         self.socket_output.append('Potion drank.\n\rYou feel much better.\n\rA small flask disintegrates.\n\r')
        #     self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))   # todo maybe: flask
