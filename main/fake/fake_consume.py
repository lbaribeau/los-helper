
from fake.fake_command import FakeCommand
from misc_functions import magentaprint

class FakeConsume(FakeCommand):
    small_flask_counter = 0

    def __init__(self, character, socket_output):
        super().__init__(socket_output)
        self.char = character
        self.inventory = character.inv
        self.large_pots = [
            'large restorative', 
            'scarlet potion', 
            'golden potion'
        ]
        self.pots = [
            'small restorative', 
            'chicken soup', 
            'white potion', 
            'small flask',
            'steel bottle', 
            'silver chalice', 
            'milky potion',
        ] + self.large_pots

    def small_flask(self, index):
        self.socket_output.append('You feel no different.\n\rPotion drank.\n\rahhhhhh\n\r')
        self.small_flask_counter = self.small_flask_counter + 1
        if self.small_flask_counter >= 3:
            self.socket_output.append("A small flask disintegrates.\r\n")
            self.inventory.remove_by_index(index)
        self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))

    # def do(self, target):
    def regular_pot(self, index):
        self.socket_output.append('Potion drank.\n\rYou feel much better.\n\rA %s disintegrates.\n\r' % self.inventory.l[index].to_string())
        self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))
        self.inventory.remove_by_index(index)

class FakeUse(FakeConsume):
    def do(self, target):
        index = self.inventory.index(target)
        magentaprint("FakeUse.do got index from inventory: {}".format(index))
        
        if index is None:
            self.socket_output.append("Use what?\n\r")
        elif self.inventory.l[index].to_string() not in self.pots + self.large_pots:
            self.socket_output.append("How does one use that?\n\r")
        else:
            if self.inventory.l[index].to_string() == 'small flask':
                self.small_flask(index)
            elif self.inventory.l[index].to_string() in self.large_pots:
                self.char.hp = self.char.hp + 10
                self.regular_pot(index)
            else:
                self.char.hp = self.char.hp + 4
                self.regular_pot(index)

class FakeDrink(FakeConsume):
    def __init__(self, character, socket_output):
        super().__init__(character, socket_output)
        self.large_pots.extend(['philtre of health'])
        self.pots.extend(['philtre of health'])

    def do(self, target):
        index = self.inventory.index(target)
        magentaprint("FakeDrink.do got index from inventory: {}".format(index))
        
        if index is None:
            self.socket_output.append("Drink what?\n\r")
        elif self.inventory.l[index].to_string() not in self.pots:
            self.socket_output.append("You can't do that.\n\r")
        else:
            if self.inventory.l[index].to_string() == 'small flask':
                self.small_flask(index)
            elif self.inventory.l[index].to_string() == 'philtre of health':
                self.socket_output.append("You drink the philtre of health's broth.\r\nThe liquid is very sweet and thick, like a syrup.\r\n")
                self.char.hp = self.char.hp + 10
                self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))
                self.inventory.remove_by_index(index)
            elif self.inventory.l[index].to_string() in self.large_pots:
                self.char.hp = self.char.hp + 10
                self.regular_pot(index)
            else:
                self.char.hp = self.char.hp + 4
                self.regular_pot(index)

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
