
import time
import sys
import json
from inspect import getframeinfo, stack

from db.Database import *

debugMode = False
verboseMode = True
startTime = datetime.now()
VERSION = "2"
#databaseFile = "maplos.db"

def get_verbose_mode():
    return verboseMode

def magentaprint(text, is_debug_command=True, log_output=False, show_hidden=False):
    global debugMode    
    # caller = getframeinfo(stack()[2][0])
    caller = []

    if debugMode:
        for st in stack():
            frame = getframeinfo(st[0])
            caller.append("{} ln {}\n".format(frame.filename, frame.lineno))

    if show_hidden:
        text = repr(text)  # escape all characters in string

    if debugMode or not is_debug_command:
        do_magentaprint(text, caller)

    if log_output:
        log = Log()
        log.data = text
        log.save()

def do_magentaprint(text, caller):
    newConsoleHandler().magenta()
    # output = str(get_timestamp() + "| <" + str(text) + ">")
    output = "{} | {} | {}".format(str(get_timestamp()), str(text), caller)

    print(output)
    newConsoleHandler().white()

def greenprint(text):
    newConsoleHandler().magenta()
    output = str(get_timestamp() + "   | " + str(text))
    print(output)
    newConsoleHandler().white()

def safe_divide(x,y):
    try:
        return x/y
    except ZeroDivisionError:
        return 0

def get_timeint():
    return datetime.now()

def get_timestamp():
    curtime = datetime.now().time().strftime("%H:%M:%S.%f")
    return curtime[:len(curtime)-5]

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

# def my_list_search(thelist, item):
#     """ Searches the list for the item and returns the index of the item.
#     Returns -1 if the item is not present"""
#     for i in range(0, len(thelist)):
#         if thelist[i] == item:
#             return i
#     return -1
    
# def my_list_equal(listA, listB):
#     lenA = len(listA)

#     if lenA != len(listB):
#         return False

#     for i in range(0, lenA):
#         if listA[i] != listB[i]:
#             return False

#     return True
    
def get_last_word(s):
    return s.rsplit(None, 1)[-1]

def get_first_word(s):
    return s.split(' ', 1)[0]

def get_shortest_array(list_of_arrays):
    shortest_array = []

    for array in list_of_arrays:
        shortest_array.append(len(array))

    index = shortest_array.index(min(shortest_array, key=int))

    return list_of_arrays[index]

def key_with_max_val(d):
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]

def flush_input():
    try:
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    except ImportError:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()

def output_api_feed(filename, data):
    with open('reporting_website/api/{}.json'.format(filename), 'w') as outfile:
        json.dump(data, outfile)

######

# TODO: These functions will belong to a 'cooldowns' object
# def wait_amount(time_triggered, period):
#     return max(time_triggered + period - time.time(), 0)

# def attack_wait(character):
#     attack_period = character.ATTACK_PERIOD_HASTE if character.HASTING else character.ATTACK_PERIOD

#     return wait_amount(character.ATTACK_CLK, attack_period)

# def wait_for_attack_ready(character):
#     time.sleep(attack_wait(character))

# def attack_ready(character):
#     return attack_wait() <= 0

# def cast_wait(character):
#     return wait_amount(character.CAST_CLK, character.CAST_WAIT)

# def wait_for_cast_ready(character):
#     time.sleep(cast_wait(character))

# def cast_ready(character):
#     return cast_wait() <= 0

# def wait_for_move_ready(character):
#     # wait_for_attack_ready(character)
#     # wait_for_cast_ready(character)
#     time.sleep(max(0, character.MOVE_WAIT - (time.time() - character.MOVE_CLK)))

# def move_ready(character):
#     return cast_ready(character) and \
#            attack_ready(character) and \
#            time.time() > character.MOVE_CLK + character.MOVE_WAIT

# def busy_loop(flag):
#     # This doesn't work because of how arguments work
#     flag = False
#     while not flag:
#         time.sleep(0.02)

###
