
from comm.ConsoleHandler import ConsoleHandler

class UnixConsoleHandler(ConsoleHandler):
    def black(self):
        print('\033[30m', end='')
    def blue(self):
        print("\033[34m", end='')
    def green(self):
        print("\033[32m", end='')
    def cyan(self):
        print("\033[36m", end='')
    def red(self):
        print("\033[31m", end='')
    def magenta(self):
        print("\033[35m", end='')
    def yellow(self):
        print("\033[33m", end='')
    def white(self):
        print("\033[37m", end='')

    #TODO: we could use something like bold(\033[1m) for bright, but there's no
    #way to reset it without also resetting the color
    #we can get around this by having this class remember its color and then reset it
    #but I'll leave that for later -kb (TODO)
    def set_bright(self):
        pass
    def set_dark(self):
        pass
