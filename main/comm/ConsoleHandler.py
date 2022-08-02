
import sys

def newConsoleHandler():
    if sys.platform == 'win32':
        from comm.WinConsoleHandler import WinConsoleHandler
        return WinConsoleHandler()
    else:
        from comm.UnixConsoleHandler import UnixConsoleHandler
        return UnixConsoleHandler()

class ConsoleHandler(object):
    ''' WinConsoleHandler and UnixConsoleHandler will inherit and implement the missing functions, 
    so this class defines an interface.'''

    # Class variable (static) shared among all objects that get made
    # So anyone who wants to print doesn't have to share and pass around one object
    # So debug mode has large scope
    debug_mode = True 

    def debug_print(self, output, **kwargs):
        self.print(output, debug_print=True, **kwargs)
    def print(self, output, debug_print=True, **kwargs):
        if (self.debug_mode and debug_print) or not debug_print:
            print(output, **kwargs)

    def blue_print(self, output, debug_print=True, **kwargs):
        self.blue();    self.print(output, debug_print, **kwargs); self.white()
    def green_print(self, output, debug_print=True, **kwargs):
        self.green();   self.print(output, debug_print, **kwargs); self.white()
    def cyan_print(self, output, debug_print=True, **kwargs):
        self.cyan();    self.print(output, debug_print, **kwargs); self.white()
    def red_print(self, output, debug_print=True, **kwargs):
        self.red();     self.print(output, debug_print, **kwargs); self.white()
    def magenta_print(self, output, debug_print=True, **kwargs):
        self.magenta(); self.print(output, debug_print, **kwargs); self.white()
    def yellow_print(self, output, debug_print=True, **kwargs):
        self.red();     self.print(output, debug_print, **kwargs); self.white()
    def white_print(self, output, debug_print=True, **kwargs):
        self.red();     self.print(output, debug_print, **kwargs); self.white()

# Idea was to create functions like this for each colo
# To make printing in color easier
# Can we make the color functions return self so we can do chain calls?
# Why not comm.ConsoleHandler.magenta().print(output).white()
# Or always switch to white after?
# We could do return self on all the functions and implement a self.print
# Now I am thinking we put the debug level variable onto the console handler
# Does that make it a singleton?
# Maybe I should read a book on OO
# How about it's a class variable



