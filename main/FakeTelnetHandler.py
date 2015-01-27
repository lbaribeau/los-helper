
class FakeTelnetHandler(object):

    def __init__(self):
        self.echoing = False

    def write(self, command):
        command += '\r'

        if self.echoing:
            print (command)

    def close(self):
        print ("totally closed that socket bruh~!")

    def read_some(self, cheatnotes="[33 H 20 M]"):
        return cheatnotes  # read_eager() would miss characters