import ctypes
# I GOT THIS FROM   http://code.activestate.com/recipes/496901/
# Was hard to find.

# See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
# for information on Windows APIs.
class WinConsoleHandler:
    
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE= -11
    STD_ERROR_HANDLE = -12

    FOREGROUND_BLUE = 0x01 # text color contains blue.
    FOREGROUND_GREEN= 0x02 # text color contains green.
    FOREGROUND_RED  = 0x04 # text color contains red.
    FOREGROUND_INTENSITY = 0x08 # text color is intensified.
    BACKGROUND_BLUE = 0x10 # background color contains blue.
    BACKGROUND_GREEN= 0x20 # background color contains green.
    BACKGROUND_RED  = 0x40 # background color contains red.
    BACKGROUND_INTENSITY = 0x80 # background color is intensified.

    __brightness = 0x00;

    __std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_color(self, color):
        """(color) -> BOOL
        
        Example: set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        """
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(self.__std_out_handle, color)
        return bool
# set_color

    def black(self):
        self.set_color(0x00 | self.__brightness)
        return
    def blue(self):
        self.set_color(self.FOREGROUND_BLUE | self.__brightness)
        return
    def green(self):
        self.set_color(self.FOREGROUND_GREEN | self.__brightness)
        return
    def cyan(self):
        self.set_color(0x03 | self.__brightness)
        return
    def red(self):
        self.set_color(self.FOREGROUND_RED | self.__brightness)
        return
    def magenta(self):
        self.set_color(0x05 | self.__brightness)
        return
    def yellow(self):
        self.set_color(0x06 | self.__brightness)
        return
    def white(self): 
        self.set_color(0x07 | self.__brightness)
        return    

# Hopefully not misleading - you have to call these BEFORE calling colors to
# have an effect.. default is dark.
    def set_bright(self):                      
        self.__brightness = 0x08
        return
    def set_dark(self):
        self.__brightness = 0x00
        return

