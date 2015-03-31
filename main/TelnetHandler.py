
import telnetlib
from socket import error

from misc_functions import magentaprint

class TelnetHandler(object):

    def __init__(self):
        self.tn = self.connect_to_MUD()

    def write(self, command):
        command += '\r'
        # magentaprint("\"" + command[:len(command)-1] + "\" ", end="")
        magentaprint("Sending '" + command[:len(command)-1] + "'")
        try:
            self.tn.write(command.encode('ascii'))
        except error:
            magentaprint("TelnetHandler write() error: " + str(error))
        # magentaprint("sent.", timestamp=False)

    def connect_to_MUD(self):
        return telnetlib.Telnet("mud.landsofstone.org", 4801)  
        # No need to call open (http://www.python.org/doc/2.5.2/lib/module-telnetlib.html)

    def close(self):
        self.tn.close()

    def get_socket(self):
        return self.tn.get_socket()

    def read_some(self):
        try:
            return self.tn.read_some()  # read_eager() would miss characters
        except error:
            magentaprint("TelnetHandler read_some() error: " + str(error))
            return ''

        
