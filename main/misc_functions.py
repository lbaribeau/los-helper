import time
import sys
from ConsoleHandler import newConsoleHandler
from datetime import datetime

debugMode = False
verboseMode = True
startTime = datetime.now()
VERSION = "2"
#databaseFile = "maplos.db"

##################################### MISC FUNCTIONS ########################

def wait_for_move_ready(character):
    #global character_inst
    time.sleep(max(0, character.MOVE_WAIT - (time.time() - character.MOVE_CLK)))
    wait_for_attack_ready(character)
    wait_for_cast_ready(character)
    return

def wait_for_attack_ready(character):
    if(character.HASTING):
        time.sleep(max(0, character.ATTACK_PERIOD_HASTE - (time.time() - character.ATTACK_CLK)))
    else:
        time.sleep(max(0, character.ATTACK_PERIOD - (time.time() - character.ATTACK_CLK)))        
    return

def wait_for_cast_ready(character):
    time.sleep(max(0, character.CAST_WAIT - (time.time() - character.CAST_CLK)))
    return

def my_list_search(thelist, item):
    """ Searches the list for the item and returns the index of the item.
    Returns -1 if the item is not present"""
    for i in range(0, len(thelist)):
        if (thelist[i] == item):
            return i
    return -1
    
def my_list_equal(listA, listB):
    lenA = len(listA)
    if(lenA != len(listB)):
        return False
    for i in range(0, lenA):
        if (listA[i] != listB[i]):
            return False
    return True
    
#def magentaprint(s, mod_s=""):
def magentaprint(text, isDebugCommand=True):
    global debugMode

    if (debugMode or not isDebugCommand):
        do_magentaprint (text)

def do_magentaprint(text):
    newConsoleHandler().magenta()

    output = str(get_timestamp() + "| " + str(text))

    print (output)

    newConsoleHandler().white()

def manage_telnet_output(text, isVerbose=True):
    global verboseMode

    if (verboseMode):
        sys.stdout.write(text)
    elif not (isVerbose):
        sys.stdout.write(text)
    return

def get_timestamp():
    curtime = datetime.now().time()
    return curtime.strftime("%H:%M:%S")

def get_runtime():
    global startTime
    runtime = datetime.now() - startTime #by not including .time() we're creating a timedelta object
    return runtime

def get_runtime_in_minutes():
    runtime = get_runtime()
    seconds = int(runtime.total_seconds()) #no millisecond nonsense please
    magentaprint("Seconds run: " + str(seconds))
    if (seconds <= 1):
        seconds = 60
    minutes = (seconds / 60) #at least display 1 minute
    return minutes

def calculate_vpm(value):
    minutes = get_runtime_in_minutes()
    vpm = int(value / minutes) #no decimals
    return vpm

def replace_newlines_with_spaces(s):
    return_string = s[:]     
    for removechar in ["\r", "\n"]:
        Nindex = return_string.find(removechar)
        while(Nindex != -1):
            if(removechar == '\r'):
                return_string = return_string[0:Nindex] + return_string[Nindex+1:]
            else:
                return_string = return_string[0:Nindex] + ' ' + return_string[Nindex+1:]
            Nindex = return_string.find(removechar)
    return return_string
