
from fake.fake_command import FakeCommand
from misc_functions import magentaprint

class FakeUse(FakeCommand):
    def __init__(self, character, socket_output):
        super().__init__(socket_output)
        self.char = character
        self.inventory = character.inv
        self.pots = [
            'small restorative', 'large restorative', 'chicken soup', 'scarlet potion', 'small flask',
            'white potion', 'steel bottle', 'silver chalice', 'milky potion'
        ]
        self.large_pots = ['large restorative', 'scarlet potion', 'philtre of health']
        self.small_flask_counter = 0

    def do(self, target):
        i = self.inventory.index(target)
        magentaprint("FakeUse.do got index from inventory: {}".format(i))
        
        if i is None:
            self.socket_output.append("Use what?\n\r")
        elif self.inventory.l[i].to_string() not in self.pots + self.large_pots:
            self.socket_output.append("How does one use that?\n\r")
        else:
            if self.inventory.l[i].to_string() == 'small flask':
                self.socket_output.append('You feel no different.\n\rPotion drank.\n\rahhhhhh\n\r')
                self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))
                self.small_flask_counter = self.small_flask_counter +1
                if self.small_flask_counter >= 3:
                    self.socket_output.append("A small flask disentegrates.")
                    self.inventory.remove_by_index(i)
                return
            elif self.inventory.l[i].to_string() in self.large_pots:
                self.char.hp = self.char.hp + 10
                self.inventory.remove_by_index(i)
            else:
                self.char.hp = self.char.hp + 4

            self.socket_output.append('Potion drank.\n\rYou feel much better.\n\rA %s disintegrates.\n\r' % self.inventory.l[i].to_string())
            self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))
            self.inventory.remove_by_index(i)

        # flask with RNG
        # if 'small flask' in self.pots:
        #     self.flask_rng = self.flask_rng + 1 % 2
        #     self.char.hp = self.char.hp + 2
        #     if self.flask_rng == 1:
        #         self.socket_output.append('Potion drank.\n\rYou feel much better.\n\r')
        #     else:
        #         self.pots.remove('small flask')
        #         self.socket_output.append('Potion drank.\n\rYou feel much better.\n\rA small flask disintegrates.\n\r')
        #     self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))   # todo maybe: flask
