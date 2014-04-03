
import time
import sys
from ConsoleHandler import newConsoleHandler
from datetime import datetime

debugMode = True
verboseMode = True

##################################### MISC FUNCTIONS ########################

def send_to_telnet(tn, text):
    text += '\r'
    tn.write(text.encode('ascii'))
    return

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

def count_occurences(thelist, item):
    """ Returns the number of occurences of item in the list."""
    count=0
    for i in range(0, len(thelist)):
        if(thelist[i]==item):
            count=count+1
    return count
    
    
def my_list_equal(listA, listB):
    lenA = len(listA)
    if(lenA != len(listB)):
        return False
    for i in range(0, lenA):
        if (listA[i] != listB[i]):
            return False
    return True
    

#def extract_sellable_and_droppable(inv_list, keep_list):
    # Now... do fix for selling the wrong thing...
    # Go through and rename things so that the bot
    # can refer to them uniquely.  Use the second word
    # more often.

    # Note: items in keep_list should not yet be removed from the 
    # inventory list.
#    return_list = []
#    unusable_words = []
    #inv_list = inv_list_in[:] # make a copy because I want to change around.
#    for i in range(0, len(inv_list)):
#        item_split = inv_list[i].split(" ")
        # There is an exception from item "two by four" which can't be
        # referred to as 'by'
#        if(my_list_search(item_split, "by") != -1):
#            item_split.remove("by")
        # exception "bolt of cloth"
#        if(my_list_search(item_split, "of") != -1):
#            item_split.remove("of")
                              
        # First check if its a keeper.
        # Then check if its the same as the prev item.
        #   If so then insert the same as the prev item (could be '' if
        #   there was not a matching string)       
#        if(my_list_search(keep_list, inv_list[i]) != -1):
            # If its in the keep list, add it to unusable words and that's it.
            # Do nothing.  However every case does that so do nothing.
#            pass
#        elif(i > 0 and inv_list[i] == inv_list[i-1]):# and
            #my_list_search(item_split, return_list[len(return_list)-1]) != -1):
#            print "Appending " + return_list[len(return_list)-1] + " because i am on " + inv_list[i] + " which is the same as " + inv_list[i-1]
#            return_list.append(return_list[len(return_list)-1])
#        elif(len(item_split) == 1):
            # It's a one-word item.
#            unique_item_string = item_split[0]
#            if(my_list_search(unusable_words, item_split[0]) == -1):
#                return_list.append(unique_item_string)
#            else:
#                print "extract_sellable_and_droppable: could not fit \"" + unique_item_string+"\""
#                return_list.append("")
#        else:
            # Its got more than one word.
#            for n in [1] + [0] + range(2, len(item_split)):
#                unique_item_string = item_split[n]
#                if(my_list_search(unusable_words, unique_item_string) == -1):
#                    return_list.append(unique_item_string)
#                    break
#                elif(n == len(item_split) - 1):
#                    return_list.append("") # add an empty string so that this
                        # remains a parallel list with SELL_LIST
#                    print "extract_sellable_and_droppable: could not fit \""+inv_list[i]+"\""
#        for s in item_split:
#            unusable_words.append(s)
#    return return_list               

def extract_sellable_and_droppable(inv_list, keep_list):
    # return a list of strings that the bot use for selling
    
    #for i in range(0, len(inv_list)):
    # Go backwards through the list because we want to sell in reverse order
    # That way the number don't change
    #for i in range(len(inv_list)-1,-1,-1):
    # Going backwards might work but I would need to nest a loop 
    # forwards through the inv_list to figure the number n to use (sell cloak n)
    list_of_string_references=_make_item_references(inv_list, keep_list)
    list_of_string_references.reverse()
    return list_of_string_references


def _make_item_references(inv_list, keep_list):
    
#    item_references = []
#    for i in range(0, len(inv_list)):
#        if(my_list_search(keep_list, inv_list[i]) == -1):
#            reference_string = _item_string_to_reference_string(inv_list[i])
#            if(my_list_search(used_strings, reference_string) != -1):
#                count = count_occurences(used_strings, reference_string)
#               item_references.append(reference_string+" "+str(count+1))
#           else:
#               item_references.append(reference_string)
#           used_strings.append(reference_string)
    reference_strings=[]
    numbered_reference_strings=[]
    for i in range(0, len(inv_list)):
        reference_strings.append(_item_string_to_reference_string(inv_list[i]))
        if(my_list_search(keep_list, inv_list[i]) == -1):
            number_of_prev_items_with_same_reference = \
                count_occurences(reference_strings, reference_strings[i])-1
            if(number_of_prev_items_with_same_reference == 0):
                numbered_reference_strings.append(reference_strings[i])
            else:
                numbered_reference_strings.append(reference_strings[i] + \
                    " " + str(number_of_prev_items_with_same_reference + 1))
            
    return numbered_reference_strings    
        
        
def _item_string_to_reference_string(item_string):
    # 'grey cloak' will change to 'grey'
    # It just takes the first word.
    return item_string.split(" ")[0].split(".")[0]



#def count_occurences(theList, theValue):
#    # Counts the occurences of theValue in theList
#    count=0
#    for i in range(0, len(theList)):
#        if (theList[i] == theValue):
#            count=count+1
#    return count   
        
    
    
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
    return time.strftime("%H:%M:%S", time.gmtime())