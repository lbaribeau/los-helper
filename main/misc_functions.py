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

# TODO: These functions will belong to a 'cooldowns' object
def wait_amount(time_triggered, period):
    return max(time_triggered + period - time.time(), 0)

def attack_wait(character):
    attack_period = character.ATTACK_PERIOD_HASTE if character.HASTING else character.ATTACK_PERIOD

    return wait_amount(character.ATTACK_CLK, attack_period)

def wait_for_attack_ready(character):
    time.sleep(attack_wait(character))

def attack_ready(character):
    return attack_wait() <= 0

def cast_wait(character):
    return wait_amount(character.CAST_CLK, character.CAST_WAIT)

def wait_for_cast_ready(character):
    time.sleep(cast_wait(character))

def cast_ready(character):
    return cast_wait() <= 0

def wait_for_move_ready(character):
    wait_for_attack_ready(character)
    wait_for_cast_ready(character)
    time.sleep(max(0, character.MOVE_WAIT - (time.time() - character.MOVE_CLK)))

def move_ready(character):
    return cast_ready(character) and \
           attack_ready(character) and \
           time.time() > character.MOVE_CLK + character.MOVE_WAIT

def busy_loop(flag):
    flag = False
    while not flag:
        time.sleep(0.02)

###

def my_list_search(thelist, item):
    """ Searches the list for the item and returns the index of the item.
    Returns -1 if the item is not present"""
    for i in range(0, len(thelist)):
        if thelist[i] == item:
            return i
    return -1
    
def my_list_equal(listA, listB):
    lenA = len(listA)

    if lenA != len(listB):
        return False

    for i in range(0, lenA):
        if listA[i] != listB[i]:
            return False

    return True
    
def magentaprint(text, isDebugCommand=True):
    global debugMode

    newConsoleHandler().magenta()
    output = str(get_timestamp() + "| " + str(text))

    if debugMode:
        print(output)
    elif not isDebugCommand:
        print(output)

    newConsoleHandler().white()

def manage_telnet_output(text, isVerbose=True):
    global verboseMode

    if verboseMode:
        sys.stdout.write(text)
    elif not isVerbose:
        sys.stdout.write(text)

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
    if seconds <= 1:
        seconds = 60
    minutes = (seconds / 60) #at least display 1 minute
    return minutes

def calculate_vpm(value):
    minutes = get_runtime_in_minutes()
    vpm = int(value / minutes) #no decimals
    return vpm

def replace_newlines_with_spaces(s):
    s = s.replace('\n\r', ' ')
    return s
