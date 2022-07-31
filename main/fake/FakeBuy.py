
from fake.fake_command import FakeCommand
from misc_functions import magentaprint, greenprint

class FakeBuy(FakeCommand):
    def __init__(self, inventory, socket_output):
        super().__init__(socket_output)
        self.inventory = inventory
        self.cant_carry = True

    def do(self, target):
        if self.cant_carry:
            self.socket_output.append("You can't carry anymore.\n\r")
        else:
            if target == 'maul':
                self.inventory.add('maul hammer')
            elif target == 'heavy':
                self.inventory.add('heavy crossbow')
            elif target == 'sabre':
                self.inventory.add('sabre')
            elif target == 'long':
                self.inventory.add('long sword')
            elif target == 'iron 2':
                magentaprint("FakeBuy iron shield")
                self.inventory.add('iron shield')
            else:
                greenprint("FakeBuy error/incomplete: Fake telnet doesn't support buying EVERYTHING\n\r")
                greenprint("FakeBuy adding %s to inventory.\n\r" % target)
                self.inventory.add(target)
            
            self.socket_output.append('Bought.\n\r')