
import telnetlib

# from ConsoleHandler import newConsoleHandler
from misc_functions import magentaprint

class TelnetHandler(object):

    def __init__(self):
        self.tn = self.connect_to_MUD()

    def write(self, command):
        command += '\r'
        # newConsoleHandler().magenta()
        magentaprint("\"" + command[:len(command)-1] + "\" ", end="")
        # print("\"" + command[:len(command)-1] + "\" ", end="")
        # print("test.", end="")
        #magentaprint("\"" + command[:len(command)-2] + "\" ")
        # newConsoleHandler().white()
        self.tn.write(command.encode('ascii'))
        # newConsoleHandler().magenta()
        # print("sent.")
        magentaprint("sent.", timestamp=False)
        # print("sent.", end="")
        # newConsoleHandler().white()

    # def magentaprint(s, end=None):
    #     newConsoleHandler().magenta()
    #     if end:
    #         print(s, end='')
    #     else:
    #         print(s)
    #     newConsoleHandler.white()

    def connect_to_MUD(self):
        return telnetlib.Telnet("mud.landsofstone.org", 4801)  
        # No need to call open (http://www.python.org/doc/2.5.2/lib/module-telnetlib.html)

    def close(self):
        self.tn.close()

    def get_socket(self):
        return self.tn.get_socket()

    def read_some(self):
        return self.tn.read_some()  # read_eager() would miss characters
