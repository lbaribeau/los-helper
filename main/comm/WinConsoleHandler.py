
# I GOT THIS FROM   http://code.activestate.com/recipes/496901/
# See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
# for information on Windows APIs.

import ctypes
from comm.ConsoleHandler import ConsoleHandler

class WinConsoleHandler(ConsoleHandler):
    STD_INPUT_HANDLE  = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE  = -12
    __brightness = 0x00
    __std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_bright(self):
        self.__brightness = 0x08
    def set_dark(self):
        self.__brightness = 0x00
    def black(self):
        self.set_color(0x00 | self.__brightness)
    def blue(self):
        self.set_color(0x01 | self.__brightness)
    def green(self):
        self.set_color(0x02 | self.__brightness)
    def cyan(self):
        self.set_color(0x03 | self.__brightness)
    def red(self):
        self.set_color(0x04 | self.__brightness)
    def magenta(self):
        self.set_color(0x05 | self.__brightness)
    def yellow(self):
        self.set_color(0x06 | self.__brightness)
    def white(self):
        self.set_color(0x07 | self.__brightness)

    def set_color(self, color_boolean):
        # Example: set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        return ctypes.windll.kernel32.SetConsoleTextAttribute(self.__std_out_handle, color_boolean)
    def colour_print(self, color_boolean, output, debug_print=True, **kwargs):
        self.set_color(color_boolean)
        self.print(output, debug_print, **kwargs)
        self.white()

    # FOREGROUND_BLACK     = 0x00 # Foreground color means the text colour
    # FOREGROUND_BLUE      = 0x01
    # FOREGROUND_GREEN     = 0x02
    # FOREGROUND_CYAN      = 0x03
    # FOREGROUND_RED       = 0x04
    # FOREGROUND_MAGENTA   = 0x05
    # FOREGROUND_YELLOW    = 0x06
    # FOREGROUND_WHITE     = 0x07
    # FOREGROUND_INTENSITY = 0x08
    # BACKGROUND_BLACK     = 0x00
    # BACKGROUND_BLUE      = 0x10
    # BACKGROUND_GREEN     = 0x20
    # BACKGROUND_CYAN      = 0x30
    # BACKGROUND_RED       = 0x40
    # BACKGROUND_MAGENTA   = 0x50
    # BACKGROUND_YELLOW    = 0x60
    # BACKGROUND_WHITE     = 0x70
    # BACKGROUND_INTENSITY = 0x80


