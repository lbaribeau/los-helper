
# I GOT THIS FROM   http://code.activestate.com/recipes/496901/
# Was hard to find.

# See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
# for information on Windows APIs.

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

brightness = 0x00;

import ctypes

std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def set_color(color, handle=std_out_handle):
    """(color) -> BOOL
    
    Example: set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    """
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool
# set_color

# win_console.py

def black():
    set_color(0x00 | brightness)
    return
def blue():
    set_color(FOREGROUND_BLUE | brightness)
    return
def green():
    set_color(FOREGROUND_GREEN | brightness)
    return
def cyan():
    set_color(0x03 | brightness)
    return
def red():
    set_color(FOREGROUND_RED | brightness)
    return
def magenta():
    set_color(0x05 | brightness)
    return
def yellow():
    set_color(0x06 | brightness)
    return
def white(): 
    set_color(0x07 | brightness)
    return    

# Hopefully not misleading - you have to call these BEFORE calling colors to
# have an effect.. default is dark.
def set_bright():                      
    global brightness
    brightness = 0x08
    return
def set_dark():
    global brightness
    brightness = 0x00
    return
