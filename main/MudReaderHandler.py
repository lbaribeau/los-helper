
import time
import re

from misc_functions import *
from MyBuffer import *


class MudReaderHandler:
    # This object tells the MudReaderThread what to do.
    # The reason it exits is because you don't want multiple 
    # threads accessing the same buffer so its important for 
    # the MudReader thread to manage that.  This handler 
    # tells the MudReader thread what needs to happen (ie that 
    # the buffer needs to be cleared).
    
    # The thread has a bunch of flags.  This object is used to set them.
    
    # The flags will belong to the thread.  Again, this handler has little 
    # substance except to know how things are done.  The flags belong to 
    # the thread.  The way it usually works is that the handler SETs a flag
    # and the thread will UNSET it (on its own time).  The thread spends a 
    # lot of its time waiting for flags.  It also waits for text to come in 
    # on the buffer.  Often a flag will be unset triggered on that text.  
    # The handlers job is to know what flags to set.
    
    def __init__(self, MudReaderThread, Character_inst_in):        
        
        self.MudReaderThread = MudReaderThread
        self.Character_inst = Character_inst_in
        self.good_MUD_timeout = 1.2  
            # A good amount of time to wait for the MUD to spit out 
            # any given text.  My goal however is to never timeout :)
    # end __init__
        
        
# These two functions are deprecated.  I really like them though.
#    def MUD_output_check(self, regex_true, regex_false="qhicndh", timeout=0.8):
#        """ This is a function that should make it a lot easier to get 
#        information from the MUD.  Pass this function a regex_true and it will 
#        return a match object (or null if there was no match) when compared to 
#        the recent MUD buffer.  This is useful if you are expecting some kind 
#        of output.  
#        Example:    tn.write("cast show-aura")
#                    M_obj = MUD_output_check("You glow with a (.+?) aura\.")
#                    aura = M_obj.group(1)
#        The second regex can be used to speed up the process if there is a regex 
#        you can use to tell if regex_true will not occur, ie:
#                    tn.write("sell grey")
#                    M_obj = MUD_output_check(
#                        "The shopkeep gives you (.+?) gold for an? (.+?)\.",
#                        "The shopkeep says, \"I won't buy that rubbish from you")
#                    if(M_obj):
#                        GOLD = GOLD + int(M_obj.group(1)
#        Note that to be thread safe only one of this function can be going at 
#        once.  """        
#        
#        self.MudReaderThread.__check_regex_true = regex_true
#        self.MudReaderThread.__check_regex_false = regex_false
#        self.MudReaderThread.__check_M_obj = None
#        self.MudReaderThread.__check_flag = True  
                    # Now the MUD output thread will start looking
                    # for those regexes.
                           
#        now = time.time()
#        while(self.MudReaderThread.__check_flag and time.time() - now < timeout):
#            time.sleep(0.05) # sleep here so it isn't a busy loop
            
#        return self.MudReaderThread.__check_M_obj
    
    
#    def wait_for_aura_match(self, timeout=self.good_MUD_timeout):               
#        if(self.character_inst.MANA >= SHOW_AURA_COST):
#            M_obj = self.MUD_output_check("You glow with a (.+?) aura\.")
#            if(M_obj):
#                self.character_inst.AURA = M_obj.group(1)
#                self.character_inst.AURA_SCALE = my_list_search(self.character_inst.AURA_LIST, self.character_inst.AURA)
#                return True
#            else:
#                return False
#        else:
#            return False
    
    
    def check_for_successful_go(self):
        # This function can be called right after going through an exit
        # to determine whether we successfully entered the next exit.
        
        # It belongs to MudReader because managing the buffer is a little 
        # bit complicated.  It's important that the buffer is CLEARED the 
        # moment that this function is called because it may still contain 
        # the description and exits of the current place.  That can lead 
        # to the incorrect conclusion that the go was successful before 
        # waiting for the MUD text for the new area.  That's where most 
        # of the complexity of this function lies.

        # Frankly its hard to see what's going on from here.  When we 
        # set the check_go_flag, the first thing the thread does is 
        # clears its buffer.  The reason for that is that 
        # check_for_successful_go could return immediately and incorrectly 
        # if the buffer is not cleared.  Then, only upon seeing new text 
        # will the Reader unset the flag, which is what we're waiting for.
        # The reader thread will set its SUCCESSFUL_GO variable which we will
        # read and return.
        
        self.Character_inst.GO_BLOCKING_MOB = ""
        self.Character_inst.GO_PLEASE_WAIT = False
        self.Character_inst.GO_NO_EXIT = False
        self.Character_inst.GO_TIMEOUT = False
        self.Character_inst.SUCCESSFUL_GO = False  

        self.MudReaderThread.CHECK_GO_FLAG = 1
            # This is like the return value.
            # Probably not necessary to set it but oh well.
        
        timeout = self.good_MUD_timeout
        start_time = time.time()
        run_time = 0
        while(self.MudReaderThread.CHECK_GO_FLAG == 1 and 
              run_time < timeout):
            time.sleep(0.05)
            run_time = time.time() - start_time
            
        #magentaprint("MudReaderHandler: Time for check_for_successful_go was %f" % run_time)
        
        # Note:  I've found these timing checks to be buggy because the OS often 
        # changes the system clock in the background.  We can't really rely on time.time() 
        # too much :(.
        if(run_time < timeout):
            #magentaprint("Check for successful go, returning " + str(self.MudReaderThread.SUCCESSFUL_GO))
            return self.Character_inst.SUCCESSFUL_GO
        else:
            magentaprint("MudReaderHandler: MudReadThread timed out on check_go by %f" % (run_time-start_time))
            self.Character_inst.GO_TIMEOUT = True
            return False

        #magentaprint(self.MudReaderThread_inst.MUD_buffer.buffer)
        

        
    
    
# Check for monsters not valie at all because we can only check 
# for text that hasn't come yet!
#    def check_for_monsters(self, timeout=5.0):
        
#        magentaprint("MudReaderHandler: check_for_monsters:starting... waiting for MUD_read")
        
#        self.MudReaderThread.MONSTER_LIST = []
#        self.MudReaderThread.MONSTER_CHECK_FLAG = 1
#        magentaprint("MudReaderHandler: Setting flag to do monster check %f" % (time.time()-self.character_inst.START_TIME))
#        start_time = time.time()
#        run_time = 0
#        while(self.MudReaderThread.MONSTER_CHECK_FLAG == 1 and 
#              (run_time < timeout)):
#            # Set the flag and wait for MUD_read_thread to do some magic.
#            # (reminds me... TBD make bot check for MUD_read_thread life and
#            # turf if necessary.
#            time.sleep(0.05)    # Do a short sleep so this busy loop doesn't
#                                # hog resources.
#            run_time = time.time() - start_time
#            
#        magentaprint("MudReaderHandler: Time for check_for_monsters was %f" % run_time)
#        magentaprint("  got " + str( self.MudReaderThread.MONSTER_LIST) + ", now parsing it.")  

#        if(run_time >= timeout):
#            timeout_amount = run_time - timeout
#            magentaprint(("MudReaderHandler: MudReaderThread timed out on check_for_monsters by %f.  Returned: " + str(self.character_inst.MONSTER_LIST)) % timeout_amount) 
            
#       if(self.MudReaderThread.MONSTER_CHECK_FLAG):
#           # This shouldn't happen
#           magentaprint("MudReaderHandler: MONSTER_CHECK_FLAG was still set.")
#           magentaprint("  Here is what we have... " + str(self.MudReaderThread.MONSTER_LIST))
#           self.MudReaderThread.MONSTER_CHECK_FLAG = 0      
        
#       magentaprint("Done parsing, returning list to 'run'")
#       return self.MudReaderThread.MONSTER_LIST

    

        
        #self.character_inst.AURA_CHECK_FLAG = 1
        #now = time.time()
        #while(self.character_inst.AURA_CHECK_FLAG == 1 and time.time() - now < 0.8):
        #    time.sleep(0.05)
        
        #tn.write("cast show-aura")
        
    def wait_for_inventory_match(self):
        #self.character_inst.INVENTORY_LIST = []
        self.MudReaderThread.CHECK_INVENTORY_FLAG = 1
        start_time = time.time()
        run_time = 0
        timeout = self.good_MUD_timeout
        while(self.MudReaderThread.CHECK_INVENTORY_FLAG == 1 and 
              run_time < timeout):
            time.sleep(0.05)
            run_time = time.time() - start_time
            
        if(run_time < timeout):
            return True
        else:
            return False    
        
    def wait_for_aura_match(self):
        self.MudReaderThread.CHECK_AURA_FLAG = 1
        start_time = time.time()
        run_time = 0
        timeout = self.good_MUD_timeout
        while(self.MudReaderThread.CHECK_AURA_FLAG == 1 and 
              run_time < timeout):
            time.sleep(0.05)
            run_time = time.time() - start_time
            
        if(run_time < timeout):
            return True
        else:
            return False  
        
    def check_if_item_was_sold(self):
        self.MudReaderThread.CHECK_SELL_FLAG = 1
        start_time = time.time()
        run_time = 0
        timeout = self.good_MUD_timeout
        while(self.MudReaderThread.CHECK_SELL_FLAG == 1 and 
              run_time < timeout):
            time.sleep(0.05)
            run_time = time.time() - start_time
            
        if(run_time < timeout):
            return self.Character_inst.MUD_RETURN_ITEM_SOLD
        else:
            magentaprint("MudReaderHandler: Sell check timed out")
            return True # Return true if it timed out
                        # That way the item won't be dropped. 
                        # Not that it matters.  It won't time out. 
         
    
        
# end MudReaderHandler class




    