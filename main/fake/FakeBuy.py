
from fake.FakeCommand import FakeCommand

class FakeBuy(FakeCommand):
    def do(self, target):
        self.socket_output.append('Bought.\n\r')