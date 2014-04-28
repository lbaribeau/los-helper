
class UnixConsoleHandler(object):

    def black(self):
        print("\033[30m")
    def blue(self):
        print("\033[34m")
    def green(self):
        print("\033[32m")
    def cyan(self):
        print("\033[36m")
    def red(self):
        print("\033[31m")
    def magenta(self):
        print("\033[35m")
    def yellow(self):
        print("\033[33m")
    def white(self):
        print("\033[37m")

    #TODO: we could use something like bold(\033[1m) for bright, but there's no
    #way to reset it without also resetting the color
    #we can get around this by having this class remember it's color and then reset it
    #but I'll leave that for later -kb (TODO)
    def set_bright(self):                      
        pass
    def set_dark(self):
        pass
