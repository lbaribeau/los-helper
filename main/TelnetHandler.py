
import telnetlib

class TelnetHandler(object):

    def __init__(self):
        self.tn = self.connect_to_MUD()
        self.echoing = False

    def write(self, command):
        command += '\r'

        if self.echoing:
            print (command)
    
        self.tn.write(command.encode('ascii'))

    def connect_to_MUD(self):
        return telnetlib.Telnet("mud.landsofstone.org", 4801)  
        # No need to call open (http://www.python.org/doc/2.5.2/lib/module-telnetlib.html)

    def close(self):
        self.tn.close()

    def get_socket(self):
        return self.tn.get_socket()

    def read_some(self):
        return self.tn.read_some()  # read_eager() would miss characters
