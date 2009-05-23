
import time
import ConsoleHandler

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

def my_list_count(thelist, item):
    """ Returns the number of occurences of item in the list.
    Assumes the list is ordered and all occurences of item are
    adjacent eachother.  """
    start_point = my_list_search(thelist, item)
    if(start_point == -1):
        return 0
    else:
        count = 0
        while(the_list[start_point] == item):
            count = count + 1
            start_point = start_point + 1
        return count
    
def my_list_equal(listA, listB):
    lenA = len(listA)
    if(lenA != len(listB)):
        return False
    for i in range(0, lenA):
        if (listA[i] != listB[i]):
            return False
    return True
    

def make_list_sellable(inv_list, keep_list):
    # Now... do fix for selling the wrong thing...
    # Go through and rename things so that the bot
    # can refer to them uniquely.  Use the second word
    # more often.

    # Note... it assumes that KEEP_LIST removal has already been done.
    # EDIT:  NO!  it needs a list where with the keepers in it too.
    return_list = []
    unusable_words = []
    #inv_list = inv_list_in[:] # make a copy because I want to change around.
    for i in range(0, len(inv_list)):
        item_split = inv_list[i].split(" ")
        # There is an exception from item "two by four" which can't be
        # referred to as 'by'
        if(my_list_search(item_split, "by") != -1):
            item_split.remove("by")
        # exception "bolt of cloth"
        if(my_list_search(item_split, "of") != -1):
            item_split.remove("of")
                              
        # First check if its a keeper.
        # Then check if its the same as the prev item.
        #   If so then insert the same as the prev item (could be '' if
        #   there was not a matching string)       
        if(my_list_search(keep_list, inv_list[i]) != -1):
            # If its in the keep list, add it to unusable words and that's it.
            # Do nothing.  However every case does that so do nothing.
            pass
        elif(i > 0 and inv_list[i] == inv_list[i-1]):# and
           #my_list_search(item_split, return_list[len(return_list)-1]) != -1):
            print "Appending " + return_list[len(return_list)-1] + " because i am on " + inv_list[i] + " which is the same as " + inv_list[i-1]
            return_list.append(return_list[len(return_list)-1])
        elif(len(item_split) == 1):
            # It's a one-word item.
            unique_item_string = item_split[0]
            if(my_list_search(unusable_words, item_split[0]) == -1):
                return_list.append(unique_item_string)
            else:
                print "make_list_sellable: could not fit \"" + unique_item_string+"\""
                return_list.append("")
        else:
            # Its got more than one word.
            for n in [1] + [0] + range(2, len(item_split)):
                unique_item_string = item_split[n]
                if(my_list_search(unusable_words, unique_item_string) == -1):
                    return_list.append(unique_item_string)
                    break
                elif(n == len(item_split) - 1):
                    return_list.append("") # add an empty string so that this
                        # remains a parallel list with SELL_LIST
                    print "make_list_sellable: could not fit \""+inv_list[i]+"\""
        for s in item_split:
            unusable_words.append(s)
    return return_list               


#def magentaprint(s, mod_s=""):
def magentaprint(s):
    ConsoleHandler.magenta()
#    if(mod_s != ""):
#        print s % mod_s
#    else:
#        print s
    debug = False
    if(debug):
        print s 
    ConsoleHandler.white()
    return
    

