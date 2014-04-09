import time
import sys
from ConsoleHandler import newConsoleHandler
from datetime import datetime

debugMode = False
verboseMode = True
startTime = datetime.now()
VERSION = "1"

##################################### MISC FUNCTIONS ########################

def wait_for_move_ready(character_inst):
    #global character_inst
    time.sleep(max(0, character_inst.MOVE_WAIT - (time.time() - character_inst.MOVE_CLK)))
    wait_for_attack_ready(character_inst)
    wait_for_cast_ready(character_inst)
    return

def wait_for_attack_ready(character_inst):
    if(character_inst.HASTING):
        time.sleep(max(0, character_inst.ATTACK_PERIOD_HASTE - (time.time() - character_inst.ATTACK_CLK)))
    else:
        time.sleep(max(0, character_inst.ATTACK_PERIOD - (time.time() - character_inst.ATTACK_CLK)))        
    return

def wait_for_cast_ready(character_inst):
    time.sleep(max(0, character_inst.CAST_WAIT - (time.time() - character_inst.CAST_CLK)))
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

    newConsoleHandler().magenta()
#    if(mod_s != ""):
#        print s % mod_s
#    else:
#        print s

    output = str(get_timestamp() + "| " + str(text))
    #output = text

    if (debugMode):
        print (output)
    elif not (isDebugCommand):
        print (output)

    newConsoleHandler().white()
    return

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
