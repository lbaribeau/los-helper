
class FakeSocketOutput(object):
    def __init__(self, text=""):
        self.text = text

    def decode(self, format="", errors=""):
        return self.text

