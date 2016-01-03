
from comm.ConsoleHandler import newConsoleHandler

class PrintMagenta(object):
    def do(self, output):
        newConsoleHandler().magenta()
        print(output)
        newConsoleHandler().white()

def magentaprint(output):
    PrintMagenta().do(output)



