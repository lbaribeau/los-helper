
from fake.FakeCommand import FakeCommand

class FakeBuy(FakeCommand):
    def __init__(self, socket_output):
        super().__init__(socket_output)
        self.cant_carry = True

    def do(self, target):
        if self.cant_carry:
            self.socket_output.append("You can't carry anymore.")
        else:
            self.socket_output.append('Bought.\n\r')