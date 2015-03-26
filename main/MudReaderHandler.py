
import time
import re

from misc_functions import *
from MyBuffer import *

class MudReaderHandler(object):
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
    # The handler's job is to know what flags to set.
    
    def __init__(self, MudReaderThread, character):        
        
        self.MudReaderThread = MudReaderThread
        self.character = character
        self.good_MUD_timeout = 8
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
#        Example:    telnetHandler.write("cast show-aura")
#                    M_obj = MUD_output_check("You glow with a (.+?) aura\.")
#                    aura = M_obj.group(1)
#        The second regex can be used to speed up the process if there is a regex 
#        you can use to tell if regex_true will not occur, ie:
#                    telnetHandler.write("sell grey")
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
#        if(self.character.MANA >= SHOW_AURA_COST):
#            M_obj = self.MUD_output_check("You glow with a (.+?) aura\.")
#            if(M_obj):
#                self.character.AURA = M_obj.group(1)
#                self.character.AURA_SCALE = my_list_search(self.character.AURA_LIST, self.character.AURA)
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
        
        self.character.GO_BLOCKING_MOB = ""
        self.character.GO_PLEASE_WAIT = False
        self.character.GO_NO_EXIT = False
        self.character.GO_TIMEOUT = False
        self.character.SUCCESSFUL_GO = False  

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
            return self.character.SUCCESSFUL_GO
        else:
            magentaprint("MudReaderHandler: check_go timed out by %.1fs." % round(run_time, 1))
            self.character.GO_TIMEOUT = True
            return False

        #magentaprint(self.MudReaderThread_inst.MUD_buffer.buffer)
        

        
    
    
# Check for monsters not valid at all because we can only check 
# for text that hasn't come yet!
#    def check_for_monsters(self, timeout=5.0):
        
#        magentaprint("MudReaderHandler: check_for_monsters:starting... waiting for MUD_read")
        
#        self.MudReaderThread.MONSTER_LIST = []
#        self.MudReaderThread.MONSTER_CHECK_FLAG = 1
#        magentaprint("MudReaderHandler: Setting flag to do monster check %f" % (time.time()-self.character.START_TIME))
#        start_time = time.time()
#        run_time = 0
#        while(self.MudReaderThread.MONSTER_CHECK_FLAG == 1 and 
#              (run_time < timeout)):
#            # Set the flag and wait for MUD_read_thread to do some magic.
#            # (reminds me... TODO make bot check for MUD_read_thread life and
#            # turf if necessary.
#            time.sleep(0.05)    # Do a short sleep so this busy loop doesn't
#                                # hog resources.
#            run_time = time.time() - start_time
#            
#        magentaprint("MudReaderHandler: Time for check_for_monsters was %f" % run_time)
#        magentaprint("  got " + str( self.MudReaderThread.MONSTER_LIST) + ", now parsing it.")  

#        if(run_time >= timeout):
#            timeout_amount = run_time - timeout
#            magentaprint(("MudReaderHandler: MudReaderThread timed out on check_for_monsters by %f.  Returned: " + str(self.character.MONSTER_LIST)) % timeout_amount) 
            
#       if(self.MudReaderThread.MONSTER_CHECK_FLAG):
#           # This shouldn't happen
#           magentaprint("MudReaderHandler: MONSTER_CHECK_FLAG was still set.")
#           magentaprint("  Here is what we have... " + str(self.MudReaderThread.MONSTER_LIST))
#           self.MudReaderThread.MONSTER_CHECK_FLAG = 0      
        
#       magentaprint("Done parsing, returning list to 'run'")
#       return self.MudReaderThread.MONSTER_LIST

    

        
        #self.character.AURA_CHECK_FLAG = 1
        #now = time.time()
        #while(self.character.AURA_CHECK_FLAG == 1 and time.time() - now < 0.8):
        #    time.sleep(0.05)
        
        #telnetHandler.write("cast show-aura")
        
    def wait_for_inventory_match(self):
        #self.character.INVENTORY_LIST = []
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
        self.MudReaderThread.CHECK_AURA_SUCCESS = 0
        start_time = time.time()
        run_time = 0
        timeout = self.good_MUD_timeout
        while(self.MudReaderThread.CHECK_AURA_FLAG == 1 and 
              run_time < timeout):
            time.sleep(0.05)
            run_time = time.time() - start_time
            
        if(run_time < timeout and self.MudReaderThread.CHECK_AURA_SUCCESS):
            return True
        else:
            return False  
        # Commented out: Doing too much here.  This function can remain the same when adding
        # the SUCCESS flag.  BotThread handles it all because, if unsuccessful, it will 
        # recast and recall this function.  This function shouldn't reloop if the cast
        # was unsuccessful.
        ## Set flag;
        ##  MudReaderThread unsets flag in two cases
        ##  1) (Success) Aura is updated
        ##  2) Spell failed (need to recast - return failure to BotThread)
        ##  Or there can be a timeout.
        ## Return value
        #self.MudReaderThread.CHECK_AURA_FLAG = 1
        #self.MudReaderThread.CHECK_AURA_SUCCESS = 0
        #while(self.MudReaderThread.CHECK_AURA_FLAG == 1):
        #    start_time = time.time()
        #    run_time = 0
        #    timeout = self.good_MUD_timeout
        #    # Wait loop
        #    while(self.MudReaderThread.CHECK_AURA_FLAG == 1 and 
        #          run_time < timeout):
        #        time.sleep(0.05)
        #        run_time = time.time() - start_time
        #        
        #    if(self.MudReaderThread.CHECK_AURA_SUCCESS):
        #        return True
        #    elif(run_time < timeout):
        #        continue; #Spell failed
        #    else:
        #        return False #timeout
        
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
            return self.character.MUD_RETURN_ITEM_SOLD
        else:
            magentaprint("MudReaderHandler: Sell check timed out")
            return True # Return true if it timed out
                        # That way the item won't be dropped. 
                        # Not that it matters.  It won't time out. 
         
    
    # Deprecated by KillThread's BotReactions
    #def watch_attack_combat(self):
    #        # Called by KillThread
    #        # Algorithm:  Just send to MudReaderHandler.watch_attack_combat(timeout).
    #        # MudReaderHandler will wait 'timeout' seconds for the attack to resolve.
    #        # The attack will resolve within 0.2 seconds or so.  
    #        # Then, however, it will also continue to wait until the attack cooldown 
    #        # is over, for any text that should make us quit.
    #        # It will return 1 for continue and 0 to quit.
    #        
    #        # This also works for the case where the player changes the target or 
    #        # stops it on his own, because that will cause a different thread 
    #        # to change self.target or to set __stopping, niether action of 
    #        # which would be undone by this algorithm.
    #        
    #        # Only call after sending a kill command.
    #    
    #    # First, wait for the regular attack info
    #    self.MudReaderThread.check_kill_flags.waitflag = True
    #          
    #    return self.poll_flag(self.MudReaderThread.check_kill_flags)
        
    
    def poll_flag(self, check_flags):
        # Poll_flag function.
        # MudReaderHandler.poll_flag manages MudReaderThread's flags and returns 
        # when something was matched.  
        # Argument: check_flags should be a MyMudWaiterFlags object
        start_time = time.time()
        run_time = 0
        timeout = self.good_MUD_timeout
        while(check_flags.waitflag == 1 and run_time < timeout):
            time.sleep(0.05)
            run_time = time.time() - start_time
            
        if(run_time < timeout):
            #magentaprint("Poll did not time out :)")
            return check_flags.returnval
        else:
            #magentaprint("MudReaderHandler: poll timed out.")
            # Note: This timeout happens on all successful attacks because MudReader doesn't 
            # look for those strings.
            return 2
        
        # Great - things are sort of working.
        # TODO next time, put a lot of combat strings into MudReaderHandler!
        # (the poll is timing out, and I want it to be deterministic if possible.)
        # Maybe it would be better to not need to poll, or at least be generic enough
        # not to need to type out all of the attack strings.
        # Currently, watch_attack_combat times out on all successful attacks...
        # Algorithm: KillThread hits command and calls watch_attack_combat, which 
        # times out because the successful attack strings aren't currently matched, 
        # but that's ok because nothing needs to happen.  Would it be better to 
        # make sure every time?  Probably, put that on the todo list I suppose.
        # Priority, low!
        
        # What about something like, wield a weapon if one breaks, or pick up a ring.
        # Should the managing objects ALWAYS expect that sort of thing and watch 
        # for it?  No.  Should MudReaderHandler send commands to telnet?  No.
        # OBSERVER PATTERN:  The bot object should register some methods with 
        # the MudReaderHandler "If this happens, do this." ie.  
        #  If "Your weapon broke!" do "wield <weapon>"
        #  If "The market official dropped a copper ring" do "wear ring"
        # MudReaderHandler can provide that.  The MudReaderTHREAD  will actually 
        # go in and execute the notify methods, but they'll still belong to the bot.
        # Or, should I keep the flagged thread handshake so that the bot thread is 
        # executing that code?  The only way for that is for the bot thread to poll and 
        # wait (watch for a ring or a weapon break every single time it's possible...)
        # Instead (MVC,) it's better to give MudReader a function to call, 
        # but not require MudReader to know about or have access to CommandHandler.
        
        # So, I think I'll do a commit, even though I lost some functionality.
        
    # Jan 2013
    # MudReaderHandler should implement register_event(regex, function_pointer)
    # Man do I ever think in C++, this idea needs to be tweaked a little.
    # It'd be nice not to have to write a whole bunch of code every time I 
    # want to match text.
    # Do I need an object for each task?
    # May as well I guess.
    # What about, register_event(regex, telnet command)
    # That would be quite ideal.  Perhaps that's a bot function though? No.
    # Since it needs a bunch of flags and stuff I think it needs to be a class 
    # that I construct for each class.  It could be something that MudReader 
    # makes.  Then MudReaderThread could loop through each one that's been 
    # registered and call notify.  So BotThread has to make all these objects.
    # The flags would belong to the objects?  No, BotThread provides the 
    # regex and telnet command, and MudReaderHandler makes the objects?  BotThread
    # should create these little guys and register them, or perhaps a BotMinion?
    # (BotMinion because it needs the authority of Bot to send commands but doesn't 
    # fit into my model of how the Bot chooses what it does - I don't want the 
    # Bot to have to make a bunch of objects...)  
    # The "function pointer" functionality actually comes from the inheritance structure:
    # Subject knows to call notify on all of the observers, but unfortunately each has 
    # to be an object.
    # So who makes them? MudReaderHandler?  It can't issue commands though.
    # BotThread has to make them because the notify function has to use CommandHandler.
    # Well, how about los-helper?  They aren't part of the thread.  
    # los-helper should make BotRoutines.  BotReactions.
    # I feel good about that!  
    # So, BotReactions class will make an object for each reaction.
    # MudReaderThread will go through a the list of reactions, match each regex in it, 
    # and call the notify of it.  
    # Flesh out the idea:
    #  BotReactions.py creates several BotReaction objects which each have a regex 
    #  and a notify function which uses CommandHandler.  The objects get registered 
    #  by MudReaderHandler.register_reaction and get added to a list owned by 
    #  MudReaderThread.  MudReaderThread doesn't have to know any of the regexes 
    #  nor notifies, just loops through all of them.
    # I hope this works!!!
    
    def register_reaction(self, botReaction):
        """ Registers the reaction in MudReaderThread's list of regexes 
        to check and call notify on."""
        # Re-registering a reaction that was just unregistered 
        # might not work.  MudReaderThread takes some time to remove it.
        if not botReaction in self.MudReaderThread.BotReactionList:
            botReaction.unregistered = False  # I think this line's redundant
            self.MudReaderThread.BotReactionList.append(botReaction)
        # magentaprint("Registered: " + str(botReaction))
        # magentaprint("Regexes: " + str(botReaction.regexes))

    def unregister_reaction(self, botReaction):
        botReaction.unregistered = True
    #   Nevermind this function, just do it manually, it's simpler

    def is_registered(self, botReaction):
        return botReaction in self.MudReaderThread.BotReactionList and not botReaction.unregistered
        
    def unregister_reactions(self):
        self.MudReaderThread.BotReactionList = []

    #def wait_for_ability_feedback(self, CoolAbility):
        # Could do a flaggy thing or reacations.  Reactions, obviously.
        # So, if we see CoolAbility.getSuccessMudText, return 1, and 
        # CoolAbility.getFailureMudText, 0, and there's also a timeout 
        # possibility.  

        # We want to generify this use case (print a command and wait for 
        # feedback,)  so have we done that enough??  MudReaderHandler.
        # doWholeCommand.  That'd need a command object w/ expected result 
        # and optional failure text.  Should be do-able.
        # pass

    def wait_for_feedback(self, success_text, failure_text):
        # Use a reaction.  It's not really a "Bot" reaction any more... but it's good 
        # to reuse code.  It should be a MUDReaction.
        # Ya... implementing notify on 'self' is the way to do this... don't use 
        # mudReaderHandler at all.
        # CoolAbilityThread:
        #  MudReaderThread.BotReactionList.append(self)

        # def notify():
        #     self.stop()
        pass
        # myReaction = GenericBotReaction()



        

# TODO
#    def check_for_text(possibility1, possibility2

    