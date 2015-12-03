
from fake.FakeCommand import FakeCommand

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
            else:
                self.inventory.add(target)
                
            self.socket_output.append('Bought.\n\r')