
import threading
from threading import Thread
import atexit 
import time
import re
import sys
import select

from misc_functions import *
from CommandHandler import *
from KillThread import *
from CastThread import *

# Constants
ASCII_ESC = 27
ASCII_m = 109

class MudReadThread ( threading.Thread ):
    # This thread watches the the MUD output and prints it to stdout.
    # Later it will match regexes and trigger some action on different
    # output, for example maintaining the experience variable, etc.
    def __init__(self, character_inst, CommandHandler_inst, tn_in):
        Thread.__init__(self)
        self.character_inst = character_inst
        self.CommandHandler_inst = CommandHandler_inst
            # The MUD output thread needs the CommandHandler in order to stop
            # the combat threads triggered on MUD output.  Epiphany:  it would
            # be better if the combat threads could call a MUD interface object
            # because the relationship now is kind of backwards (the threads are
            # really using the MudHandler and not the other way around.)
        self.tn = tn_in
        
        # Variables used for the MUD_output_check function
        self.__check_regex_true = ""
        self.__check_regex_false = ""
        self.__check_M_obj = None
        self.__check_flag = False 
        
        self.__stopping = False
        self.__buffersize = 500      # Constant for how much to hold in buffer
                                    # which is compared to REs.  Needs to be pretty
                                    # big or I'll miss triggers.  (theoretically twice the
                                    # size of any string that I try to match to)
        atexit.register(self.stop)
    # end __init__

    def stop(self):
        self.__stopping = True
    # end stop        

    def run (self):
#        global HASTING
#        global PREV_COMMAND
#        global PREV_USER_COMMAND
#        global CAST_CLK
#        global ATTACK_CLK
#        global MOVE_CLK #not used i think
 #       global KillThread_inst # not necessary?
 #       global CastThread_inst
#        global WEAPON1
#        global WEAPON2
        # Bot variables
#        global MONSTER_CHECK_FLAG
#        global MONSTER_LIST
#        global HEALTH
#        global MANA
#        global INVENTORY_CHECK_FLAG
#        global INVENTORY_LIST
#        global SELL_CHECK_FLAG
#        global MUD_RETURN_ITEM_SOLD
#        global EXPERIENCE
#        global GOLD
#        global MOBS_JOINED_IN
#        global CHECK_GO_FLAG
#        global SUCCESSFUL_GO
#        global BLOCKING_MOB
#        global AURA_CHECK_FLAG
#        global AURA_LIST
#        global AURA
#        global AURA_SCALE
        
        
        # First get the file descriptor (no) of the internal telnet socket object
        # so we can watch for input.        
        tn_sno = self.tn.get_socket()

        MUD_buffer = "" # MUD_buffer is a string of size 80
        
        # Loop forever, just do stuff when the socket says its ready.
        while (not self.__stopping):
            currently_escaping = False  # Used to filter escape sequences
            sel_out_triple = select.select([tn_sno], [], [], 2)
            if(sel_out_triple != ([], [], [])):
                # Read some characters.  
                try:
                    fragment = self.tn.read_very_eager() # read_eager misses characters
                except EOFError:
                    print("MUD_read_thread: Exiting (saw EOF)")
                    self.stop()
                    break
                
                # There seems to be some escape sequence code which I
                # am going to filter out.  Sorry if it doesn't make sense.
                # If you are trying to read it, also remember that
                # currently_escaping may remain false over top of a loop
                # iteration.  EDIT:  They're ANSI escape codes (read wikipedia)
                character_list = list(fragment)
                out_str = ""
                escape_sequence = ""
                for c in character_list:
                    if ord(c) == ASCII_ESC:
                        currently_escaping = True
                        escape_sequence = ""
                    if not currently_escaping:             
                        out_str = out_str + c
                    if currently_escaping and ord(c) == ASCII_m:
                        escape_sequence = escape_sequence + c
                        currently_escaping = False
                        # Finished an escape sequence... change color.
                        #escape_sequence = escape_sequence[1:5] # Clip esc character
                        #sys.stdout.write(escape_sequence) # Debug
                        # Print all the stuff in buffer from before the esc
                        sys.stdout.write(out_str)
                        MUD_buffer = MUD_buffer + out_str
                        out_str = ""
                        self.set_colour(escape_sequence);  # Call subroutine to do this.
                    else:
                        escape_sequence = escape_sequence + c
                # Check for some colors.
                        
                # Print to console.
                sys.stdout.write(out_str)   # Not using print because
                                            # it inserts extra spaces.
                #sys.stdout.write("/"+out_str)  # ADDED PRINT TO BOTTOM END
                                            
                # Debug:  Print ascii out!  (doesn't do every character)
                #for i in range(0, len(out_str)):
                #    sys.stdout.write(str(ord(out_str[i])) + ' ')

                # Store that in the buffer.  
                MUD_buffer = MUD_buffer + out_str
                # Trim buffer if its too long.
                L = len(MUD_buffer)
                if(L >= self.__buffersize):
                    MUD_buffer = MUD_buffer[L-self.__buffersize+1:L]
                #print "<REPRINT>"+MUD_buffer+"<\REPRINT>"



                ###### Now match the buffer with some REs  #######
                MUD_buffer_trunc = 0
                in_combat = self.CommandHandler_inst.KillThread_inst != None and self.CommandHandler_inst.KillThread_inst.is_alive()

                
                M_obj = re.search("You feel yourself moving faster",MUD_buffer)
                if(M_obj != None):
                    self.character_inst.HASTING = True
                    self.character_inst.ATTACK_WAIT = self.character_inst.ATTACK_PERIOD_HASTE
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                M_obj = re.search("You're already hastened",MUD_buffer)
                #TBD: Its still possible that haste state is invalid.  Here user types
                #haste and I trigger on "You're already hastened"... can by improved by
                #doing everything under covers! (maybe send a command to telnet and use
                #the response to update variables but don't print anything!  This could
                #be a thread.  Or I could cover all the cases that invalidate haste,
                #which is mainly logging in.  TBD: Login_Update() (do with main thread
                #before raw_input call.)
                if(M_obj != None):
                    self.character_inst.HASTING = True
                    self.character_inst.ATTACK_WAIT = self.character_inst.ATTACK_PERIOD_HASTE
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                M_obj = re.search("You feel slower",MUD_buffer)
                if(M_obj != None):
                    self.character_inst.HASTING = False
                    self.character_inst.ATTACK_WAIT = self.character_inst.ATTACK_PERIOD
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                      
                if (re.search("That spell does not exist", MUD_buffer) or
                        re.search("You don't know that spell", MUD_buffer) or
                        re.search("You cannot meet the casting cost!", MUD_buffer) or  #Fix when I have mana available.
                        re.search("Spell name is not unique", MUD_buffer) or
                        re.search("Your spell fails", MUD_buffer) or
                        re.search("Cast what", MUD_buffer)):
                    # Unset cast wait timer if it turns out no spell was cast

                    #NOTE:  A spell failing is fine!  You can cast again right away.
                    #Probably don't want to do that automatically though.
                    #self.character_inst.CAST_CLK = -self.character_inst.CAST_WAIT  # Walking waits for CAST_CLK, and you can walk so reset that
                    self.character_inst.CAST_CLK = time.time() - self.character_inst.CAST_WAIT # reset cast clock
                    
                    #MUD_buffer = MUD_buffer[ #Not bothering with match object.
                    # This might get called a few times since I'm too lazy save
                    # the match object and find out where to cut.
                    
                    # Stop the cc command because we don't want to try again.
                    if(not re.search("Your spell fails", MUD_buffer)):                        
                        self.CommandHandler_inst.stop_CastThread()
                        
                # Set WEAPON1
                M_obj = re.search("You wield (.*?)\.", MUD_buffer)
                if (M_obj != None and not re.search(" in your off hand", M_obj.group(1))):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    weap1 = M_obj.group(1)
                    # Clip the "a " or the "some "
                    if(re.match("a ", weap1)):
                        weap1 = weap1[2:]
                    elif(re.match("some ", weap1)):
                        weap1 = weap1[5:]
                    self.character_inst.WEAPON1 = weap1
                # Set WEAPON2
                M_obj = re.search("You wield (.*?) in your off hand\.", MUD_buffer)
                if (M_obj != None):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    weap2 = M_obj.group(1)
                    if(re.match("a ",weap2)):
                        weap2 = weap2[2:]
                    elif(re.match("some ",weap2)):
                        weap2 = weap2[5:]
                    self.character_inst.WEAPON2 = weap2
                # Prompt
                M_obj = re.search("\[(.*?) H (.*?) M\]", MUD_buffer)
                if (M_obj):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    # The exception is if there's a glitch in the ANSI code or
                    # character order... happens sometimes.  (Think its the
                    # MUD's fault)  Its not critical, and I don't know how to
                    # recover from it anyway.
                    try:
                        self.character_inst.HEALTH = int(M_obj.group(1))
                        self.character_inst.MANA = int(M_obj.group(2))
                    except ValueError:
                        pass
                        
                # Do some gold stuff.
                # On gold pickup:
                M_obj = re.search("You now have (.+?) gold coins", MUD_buffer)
                if(M_obj):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    self.character_inst.GOLD = int(M_obj.group(1))
                # On tip drop:                    
                M_obj = re.search("You have (.+?) gold\.", MUD_buffer)
                if(M_obj):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    self.character_inst.GOLD = int(M_obj.group(1))
                # On vendor:
                # Also manage the sell check flag (signal to bot)
                M_obj = re.search("(?s)The shopkeep gives you (.+?) gold for (an?|some) (.+?)\.", MUD_buffer)
                if(M_obj):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    self.character_inst.GOLD = self.character_inst.GOLD + int(M_obj.group(1))
                    if(self.character_inst.SELL_CHECK_FLAG == 1):
                        self.character_inst.MUD_RETURN_ITEM_SOLD = True
                        self.character_inst.SELL_CHECK_FLAG = 0
                # Check the negative case for the sell check flag.
                if(self.character_inst.SELL_CHECK_FLAG == 1):
                    if(re.search("(?s)The shopkeep won't buy that from you\.", MUD_buffer) or
                       re.search("(?s)It isn't empty!", MUD_buffer) or
                       re.search("(?s)The shopkeep says, \"I won't buy that rubbish from you\.\"", MUD_buffer) or
                       re.search("(?s)Sell what\?", MUD_buffer)):
                        self.character_inst.MUD_RETURN_ITEM_SOLD = False
                        self.character_inst.SELL_CHECK_FLAG = 0
                #if(SELL_CHECK_FLAG == 1):
                #    M_obj = re.search("(?s)The shopkeep gives you (.+?) for a (.+?)\.", MUD_buffer)
                #    if(M_obj):
                #        MUD_RETURN_ITEM_SOLD = True
                #        SELL_CHECK_FLAG = 0
                #        GOLD = GOLD + int(M_obj.group(1))
                #        MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                        # M_obj.group(2) makes item sold accessible but
                        # that won't be required.
                #    if(re.search("(?s)The shopkeep won't buy that from you\.", MUD_buffer) or
                #       re.search("(?s)It isn't empty!", MUD_buffer)):
                #       MUD_RETURN_ITEM_SOLD = False
                #       SELL_CHECK_FLAG = 0                       

                ########    Do some monster stuff.    ######
                s_numbered = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?"
                
                # Monster is killed
                #M_obj = re.search("Your enemy, the" + s_numbered + " (.+?) has been defeated\.", MUD_buffer)            
                M_obj = re.search("Your attack overwhelms the" + s_numbered + " (.+?) and (s?he|it) collapses!", MUD_buffer)
                if(M_obj != None):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    if(my_list_search(self.character_inst.MONSTER_LIST, M_obj.group(2)) != -1):
                        magentaprint( "Removing " + M_obj.group(2) + " from MONSTER_LIST")
                        self.character_inst.MONSTER_LIST.remove(M_obj.group(2))
                    self.CommandHandler_inst.stop_KillThread()
                    self.CommandHandler_inst.stop_CastThread()
                # Monster flees... 
                #TBD chasing function.
                M_obj = re.search("The" + s_numbered + " (.+?) flees to the (.+?)\.", MUD_buffer)
                if(M_obj):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    if(my_list_search(self.character_inst.MONSTER_LIST, M_obj.group(2)) != -1):
                        magentaprint("Removing " + M_obj.group(2) + " from MONSTER_LIST")
                        self.character_inst.MONSTER_LIST.remove(M_obj.group(2))
                    self.CommandHandler_inst.stop_KillThread()
                    self.CommandHandler_inst.stop_CastThread()
                # Stop combat threads on "You don't see that here"
                M_obj = re.search("You don't see that here",MUD_buffer)
                # I don't like PREV_COMMAND.
                # "You don't see that here" needs to terminate kk because
                # MONSTER_LIST can be wrong if a mob arrives at the same time
                # as I leave an area.  So I'm removing prev command and
                # combat will always be stopped on "You don't see that here
                #prev_cmd_kill = re.match("k ",PREV_COMMAND)
                #if(M_obj != None and prev_cmd_kill != None):
                if(M_obj != None):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    if(in_combat):
                        #MONSTER_LIST = [] # bug fix for bot where mobs arrive at the last second.
                        self.CommandHandler_inst.stop_KillThread()
                        in_combat = False
                        self.character_inst.ATTACK_CLK = time.time()-self.character_inst.ATTACK_WAIT
                            #unset attack timer which would prevent action.                
                # Monster wanders to specific exit
                M_obj = re.search("The" + s_numbered + " (.+?) just wandered to the .+?\.", MUD_buffer)
                if(M_obj):
                    magentaprint( "Matched " + M_obj.group(2))
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    if(my_list_search(self.character_inst.MONSTER_LIST, M_obj.group(2)) != -1):
                        self.character_inst.MONSTER_LIST.remove(M_obj.group(2))
                # Monster wanders away
                M_obj = re.search("The" + s_numbered + " (.+?) just wandered away\.", MUD_buffer)
                if(M_obj):
                    magentaprint( "Matched " + M_obj.group(2))
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    if(my_list_search(self.character_inst.MONSTER_LIST, M_obj.group(2)) != -1):
                        self.character_inst.MONSTER_LIST.remove(M_obj.group(2))
                M_obj = re.search("An? (.+?) just arrived\.", MUD_buffer)
                if(M_obj):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    self.character_inst.MONSTER_LIST.append(M_obj.group(1))
                M_obj = re.search("You gain (.+?) experience\.", MUD_buffer)       
                if(M_obj):
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    self.character_inst.EXPERIENCE = self.character_inst.EXPERIENCE + int(M_obj.group(1))
                # Monsters joining in
                #join_in_regex = "the" + s_numbered + " (.+?) joins in the fight!"
                #M_obj = re.search(joinin_regex, MUD_buffer)
                #if(M_obj):
                #    new_trunc = M_obj.end()
                #    MUD_buffer_trunc = max([MUD_buffer_trunc, new_trunc])
                #    MOBS_JOINED_IN.append(M_obj.group(2))
                #    temp_buf = MUD_buffer[new_trunc:] # copy buffer.
                #    next_match_obj = re.search(join_in_regex, temp_buf)
                #    while(next_match_obj):
                #        new_trunc = new_trunc + second_match_obj
                #        MUD_buffer_trunc = max([MUD_buffer_trunc, new_trunc])
                #        MOBS_JOINED_IN.append(next_match_obj.group(2))
                #        temp_buf = temp_buf[new_trunc:]
                #        next_match_obj = re.search(join_in_regex, temp_buf)

                # Monsters joining in
                # Two strings which can occur
                # This one is for when a mob that is present starts fighting
                join_in_regex = "the" + s_numbered + " (.+?) joins in the fight!"
                M_obj = re.search(join_in_regex, MUD_buffer)
                new_trunc = 0
                temp_buf = MUD_buffer[:] # copy
                # Need to check for multiple matches here.
                while(M_obj):
                    new_trunc = new_trunc + M_obj.end()
                    MUD_buffer_trunc = max([MUD_buffer_trunc, new_trunc])
                    self.character_inst.MOBS_JOINED_IN.append(M_obj.group(2))
                        # Note... this thread just appends... let the bot
                        # remove stuff.  It knows better than me trying
                        # to trigger on some output.
                    temp_buf = temp_buf[new_trunc:]
                    M_obj = re.search(join_in_regex, temp_buf)
                    
                # This other string occurs when a mob wanders in and joins the fight    
                second_join_in_regex = "the" + s_numbered + " (.+?) decides to join in on the fight!"
                M_obj = re.search(second_join_in_regex, MUD_buffer)
                new_trunc = 0
                temp_buf = MUD_buffer[:] # copy
                while(M_obj):
                    new_trunc = new_trunc + M_obj.end()
                    MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                    self.character_inst.MOBS_JOINED_IN.append(M_obj.group(2))
                    temp_buf = temp_buf[new_trunc:]
                    M_obj = re.search(second_join_in_regex, temp_buf)
                    
                # Bot wants to know what monsters are present.
                # Assume he already typed look.
                if(self.character_inst.MONSTER_CHECK_FLAG == 1):
                    
                    #M_obj = re.search("You see ((.+?),)+?\.", MUD_buffer)
                    # Better read about M_obj.group and M_obj.groups.  Looks
                    # like I can't get at all the matches if I match with a
                    # '+'.  I might have to figure out how many mobs there will
                    # be by counting commas, then form my RE dynamically.
                    # Start off by getting one line starting with "You see"

                    #M_obj = re.search("(?s)You see .+\.", MUD_buffer)  # Match multlines
                    M_obj = re.search("(?s)Obvious exits: .+?\.\n\r(You see .+?\.)", MUD_buffer)  # Match multlines                    
                    #print "Matching to (?s)You see .+\."
                    if(M_obj != None):
                        MUD_mob_str = M_obj.group(1)
                        #print "Got a match!"
                        num_commas = MUD_mob_str.count(',')
                        #print "num_commas" + str(num_commas)
                        num_monsters = num_commas + 1
                        # Take out \n's and \r's
                        #print MUD_mob_str
                        MUD_mob_str = replace_newlines_with_spaces(MUD_mob_str)
                        my_monster_regex = "You see " 
                        for i in range(1,num_commas+1):
                            # Add a regex group for each mob, and nab the comma
                            # and space afterwards too.
                            my_monster_regex = my_monster_regex + "(.+?), " 
                        my_monster_regex = my_monster_regex + "(.+?)\." 
                        #print "my_monster_regex: " + my_monster_regex
                        match_monsters = re.match(my_monster_regex, MUD_mob_str)
                        for i in range(1, num_monsters+1):
                            self.character_inst.MONSTER_LIST.append(match_monsters.group(i))
                        MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                        #MUD_buffer = MUD_buffer[M_obj.end():]
                        self.character_inst.MONSTER_CHECK_FLAG=0  # Okay to unset here because we've seen all the
                            # monsters by now.
                        #print "Unsetting MONSTER_CHECK_FLAG"
                        magentaprint( "Assigned MONSTER_LIST: " + str(self.character_inst.MONSTER_LIST))
                            
                    # Now do a case where I know that there are no monsters
                    # This occurs if I see "Obvious exits: ....\n\n"
                    
                    # Note that if there are items present but no monsters
                    # I can't detect it and the bot will just have to time out
                    # or something.

                    # With some investigation, this MUD does linefeed then
                    # carriage return!!
                    M_obj = re.search("Obvious exits: .+?\.\n\r\n\r", MUD_buffer)
                    if(M_obj):
                        #magentaprint("(Debug): No monsters present (\\n\\r")
                        MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                        self.character_inst.MONSTER_CHECK_FLAG = 0
                    M_obj = re.search("It's too dark to see.", MUD_buffer)
                    if(M_obj):
                        MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                        self.character_inst.MONSTER_CHECK_FLAG = 0
                #else:
                    # Clear list if "You see... " because there are cases where
                    # something can arrive while the bot is on the way out or
                    # some such thing and MONSTER_LIST is invalid, causing the
                    # bot to swing at air.  This was better when the removal
                    # was in the bot, but that had an error once when something
                    # wandered away when I was about to engage it.
                    #M_obj = re.search("(?s)You see .+\.", MUD_buffer)  # Match multlines
                    #if(re.search("(?s)Obvious exits:", MUD_buffer) or
                    #   re.search("(?s)You see ", MUD_buffer)):
                    #    self.character_inst.MONSTER_LIST = []
                    
                #     Clear the monster list if I see Obvious exits followed by an empty
                #     line.  However, this isn't rigorous because there could be items.
                #    M_obj = re.search("(?s)Obvious exits: .+?\.\n\r\n\r", MUD_buffer)
                #    if(M_obj):
                #        MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
                #        self.character_inst.MONSTER_LIST = []                        


                # Bot wants to know if we left the room or not.
                # Note:  The following do NOT clear the buffer!  
                # There is no danger of matching twice because the 
                # check_go_flag is unset afterwards.  The buffer must 
                # remain because the bot is about to look for monsters, 
                # an operation which needs the same buffer contents.
                if(self.character_inst.CHECK_GO_FLAG == 1):
                    if(re.search("(?s)Obvious exits: ", MUD_buffer) or
                       re.search("It's too dark to see", MUD_buffer)):
                        magentaprint("MUD_READ: successful go")
                        self.character_inst.BLOCKING_MOB = ""
                        self.character_inst.SUCCESSFUL_GO = True
                        # Determined that we left an area: this is the place to 
                        # clear the monster list!
                        magentaprint("Clearing monster list, was:" + str(self.character_inst.MONSTER_LIST))
                        self.character_inst.MONSTER_LIST = []
                        self.character_inst.CHECK_GO_FLAG = 0
                    M_obj = re.search("The" + s_numbered + " (.+?) blocks your exit\.", MUD_buffer)
                    if(M_obj):
                        magentaprint("MUD_READ: unsuccessful go")
                        self.character_inst.BLOCKING_MOB = M_obj.group(2)  # Problem... what if its not the 1st mob blocking???
                        self.character_inst.SUCCESSFUL_GO = False
                        self.character_inst.CHECK_GO_FLAG = 0
                    M_obj = re.search("Please wait 1 more second\.", MUD_buffer)
                    if(M_obj):
                        magentaprint("MUD_READ: unsuccessful go (please wait)")
                        self.character_inst.BLOCKING_MOB = ""
                        self.character_inst.SUCCESSFUL_GO = False
                        self.character_inst.CHECK_GO_FLAG = 0
                    M_obj = re.search("You can't go that way\.", MUD_buffer)
                    if(M_obj):
                        # This one is pretty problematic... as it should never happen.
                        # Means we're off course.
                        magentaprint("MUD_READ: unsuccessful go (you can't go that way)")
                        self.character_inst.BLOCKING_MOB = ""
                        self.character_inst.SUCCESSFUL_GO = False
                        self.character_inst.CHECK_GO_FLAG = 0
                    M_obj = re.search("I don't see that exit\.", MUD_buffer)
                    if(M_obj):
                        magentaprint("MUD_READ: unsuccessful go (you can't go that way)")
                        self.character_inst.BLOCKING_MOB = ""
                        self.character_inst.SUCCESSFUL_GO = False
                        self.character_inst.CHECK_GO_FLAG = 0

#                if(self.character_inst.AURA_CHECK_FLAG):
                    # Bot wants to know current aura.
#                    M_obj = re.search("You glow with an? (.+?) aura.", MUD_buffer)
                    # Note though that the MUD never says 'an' here
#                    if(M_obj):
#                        MUD_buffer_trunc = max([MUD_buffer_trunc, M_obj.end()])
#                        self.character_inst.AURA = M_obj.group(1)
#                        self.character_inst.AURA_SCALE = my_list_search(self.character_inst.AURA_LIST, self.character_inst.AURA)
#                        if(self.character_inst.AURA_SCALE == -1):
#                            magentaprint('Error in reading aura (not in list), came out as ' + AURA + '.')
#                        self.character_inst.AURA_CHECK_FLAG = 0
                
                # Internal check function MUD_output_check
                if(self.__check_flag):
                    M_obj = re.search(self.__check_regex_true, MUD_buffer)
                    if(M_obj):
                        self.__check_M_obj = M_obj
                        self.__check_flag = False
                    M_obj = re.search(self.__check_regex_false, MUD_buffer)
                    if(M_obj):
                        self.__check_M_obj = None
                        self.__check_flag = False
                    

                if(self.character_inst.INVENTORY_CHECK_FLAG == 1):
                    M_obj = re.search("(?s)You have: (.+?)\.", MUD_buffer)
                    if(M_obj):
                        # Now match it.  Have to do the same as MONSTER_LIST 
                        # where I count commas...
                        # I won't have to worry about You have: if I take the group 
                        # already obtained in M_obj... actually I might even be able 
                        # to get off really easy with a split!!
                        self.character_inst.INVENTORY_LIST = []
                        inv_string = M_obj.group(1)
                        # Replace newlines with spaces
                        inv_string = replace_newlines_with_spaces(inv_string)
                        # Use split to break into a list of strings
                        #print inv_string
                        inv_list = inv_string.split(',')
                        #print inv_list
                        for i in range(0, len(inv_list)):
                            inv_list[i] = inv_list[i].lstrip()
                            inv_list[i] = inv_list[i].rstrip()
                            print inv_list[i]
                            print i
                            sys.stdout.write("Appending... ")
                            # How should I do quantities?  It probably makes sense 
                            # just to have duplicate items in the actual list
                            if(inv_list[i][0:2] == "a "):
                                inv_list[i] = inv_list[i][2:]
                                self.character_inst.INVENTORY_LIST.append(inv_list[i])
                                sys.stdout.write(inv_list[i] + '\n')
                            elif(inv_list[i][0:3] == "an "):
                                inv_list[i] = inv_list[i][3:]
                                self.character_inst.INVENTORY_LIST.append(inv_list[i])
                                sys.stdout.write(inv_list[i] + '\n')
                            elif(inv_list[i][0:5] == "some "):
                                inv_list[i] = inv_list[i][5:]
                                self.character_inst.INVENTORY_LIST.append(inv_list[i])    
                                sys.stdout.write(inv_list[i] + '\n')                        
                            # In doing quantities, may as well use insert and keep
                            # the list ordered.
                            elif(inv_list[i][0:4] == "two "):
                                sys.stdout.write("   In two...   ")
                                if(inv_list[i][0:12] == "two sets of "):
                                    inv_list[i] = inv_list[i][12:]
                                else:
                                    inv_list[i] = inv_list[i][4:]
                                    # Remove the 's' if its there
                                    if(inv_list[i][len(inv_list[i])-1] == 's'):
                                        if(inv_list[i][len(inv_list[i])-3:] == "ses" or
                                           inv_list[i][len(inv_list[i])-3:] == "xes"):
                                            inv_list[i] = inv_list[i][:len(inv_list[i])-2]                                            
                                        else:
                                            inv_list[i] = inv_list[i][:len(inv_list[i])-1]
                                for j in range(0,2):
                                    self.character_inst.INVENTORY_LIST.append(inv_list[i])
                                sys.stdout.write(str(inv_list[i]) + '\n')
                                #inv_list.insert(i, inv_list[i]) # check this
                            elif(inv_list[i][0:6] == "three "):
                                sys.stdout.write("   In three...   ")
                                if(inv_list[i][0:14] == "three sets of "):
                                    inv_list[i] = inv_list[i][14:]
                                else:
                                    inv_list[i] = inv_list[i][6:]
                                    # Remove the 's' if its there
                                    if(inv_list[i][len(inv_list[i])-1] == 's'):
                                        if(inv_list[i][len(inv_list[i])-3:] == "ses" or
                                           inv_list[i][len(inv_list[i])-3:] == "xes"):
                                            inv_list[i] = inv_list[i][:len(inv_list[i])-2]
                                        else:
                                            inv_list[i] = inv_list[i][:len(inv_list[i])-1]
                                for j in range(0,3):
                                    #inv_list.insert(inv_list[i], i) # check this
                                    self.character_inst.INVENTORY_LIST.append(inv_list[i])
                                sys.stdout.write(str(inv_list[i]) + '\n')
                            elif(inv_list[i][0:5] == "four "):
                                sys.stdout.write("   In four...   ")
                                if(inv_list[i][0:13] == "four sets of "):
                                    inv_list[i] = inv_list[i][13:]
                                else:
                                    inv_list[i] = inv_list[i][5:]
                                    # Remove the 's' if its there
                                    if(inv_list[i][len(inv_list[i])-1] == 's'):
                                        if(inv_list[i][len(inv_list[i])-3:] == "ses" or
                                           inv_list[i][len(inv_list[i])-3:] == "xes"):
                                            inv_list[i] = inv_list[i][:len(inv_list[i])-2]
                                        else:
                                            inv_list[i] = inv_list[i][:len(inv_list[i])-1]
                                for j in range(0,4):
                                    #inv_list.insert(inv_list[i], i) # check this
                                    self.character_inst.INVENTORY_LIST.append(inv_list[i])
                                sys.stdout.write(str(inv_list[i]) + "\n")
                            elif(inv_list[i][0:5] == "five "):
                                sys.stdout.write("   In five...   ")
                                if(inv_list[i][0:13] == "five sets of "):
                                    inv_list[i] = inv_list[i][13:]
                                else:
                                    inv_list[i] = inv_list[i][5:]
                                    # Remove the 's' if its there
                                    if(inv_list[i][len(inv_list[i])-1] == 's'):
                                        if(inv_list[i][len(inv_list[i])-3:] == "ses" or
                                           inv_list[i][len(inv_list[i])-3:] == "xes"):
                                            inv_list[i] = inv_list[i][:len(inv_list[i])-2]
                                        else:
                                            inv_list[i] = inv_list[i][:len(inv_list[i])-1]
                                for j in range(0,5):
                                    #inv_list.insert(inv_list[i], i) # check this
                                    self.character_inst.INVENTORY_LIST.append(inv_list[i])
                                sys.stdout.write(str(inv_list[i]) + '\n')
                            # TBD go up to fifteen.  Maybe find a more scalable way to 
                            # do it.
                            else:
                                print "BIG FAT ELSE"
                                
                        #INVENTORY_LIST = inv_list
                        self.character_inst.INVENTORY_CHECK_FLAG = 0
                    ConsoleHandler.white()
                    # end if(INVENTORY_CHECK_FLAG)


                #sys.stdout.write('"' + MUD_buffer[MUD_buffer_trunc] + '"') #debug.  Shows where last match took place.
                MUD_buffer = MUD_buffer[MUD_buffer_trunc:]
                
            else:  # sel_out_triple timed out.  (happens every  2 sec w/o input)
                # Timed out (happens every second where we didn't get input
                # Check if connection is still live and all that
                pass

    # end run

    def MUD_output_check(self, regex_true, regex_false="qhicndh", timeout=0.8):
        """ This is a function that should make it a lot easier to get 
        information from the MUD.  Pass this function a regex_true and it will 
        return a match object (or null if there was no match) when compared to 
        the recent MUD buffer.  This is useful if you are expecting some kind 
        of output.  
        Example:    tn.write("cast show-aura")
                    M_obj = MUD_output_check("You glow with a (.+?) aura\.")
                    aura = M_obj.group(1)
        The second regex can be used to speed up the process if there is a regex 
        you can use to tell if regex_true will not occur, ie:
                    tn.write("sell grey")
                    M_obj = MUD_output_check(
                        "The shopkeep gives you (.+?) gold for an? (.+?)\.",
                        "The shopkeep says, \"I won't buy that rubbish from you")
                    if(M_obj):
                        GOLD = GOLD + int(M_obj.group(1)
        Note that to be thread safe only one of this function can be going at 
        once.  """        
        
        self.__check_regex_true = regex_true
        self.__check_regex_false = regex_false
        self.__check_M_obj = None
        self.__check_flag = True  # Now the MUD output thread will start looking
                                # for those regexes.
                           
        now = time.time()
        while(self.__check_flag and time.time() - now < timeout):
            time.sleep(0.05) # sleep here so it isn't a busy loop
            
        return self.__check_M_obj
        

    def set_colour(self,ANSI_escape_sequence):
        """ This routine takes an ANSI escape sequence as an argument and
        calls the ConsoleHandler class routines to have the windows console react."""
        bright_char = ANSI_escape_sequence[2]
        colour_char = ANSI_escape_sequence[3]
        if(bright_char == '3'):
            ConsoleHandler.set_dark()
        elif(bright_char == '4'):
            ConsoleHandler.set_bright()
        else:
            y=1 # do nothing
        # Maybe check if character 2 is a '3' or '4' which designate colour
        # commands but I'm too lazy.
        if(colour_char == '0'):
            ConsoleHandler.black()
        elif(colour_char == '1'):
            ConsoleHandler.red()
        elif(colour_char == '2'):
            ConsoleHandler.green()
        elif(colour_char == '3'):
            ConsoleHandler.yellow()
        elif(colour_char == '4'):
            ConsoleHandler.blue()
        elif(colour_char == '5'):
            ConsoleHandler.magenta()
        elif(colour_char == '6'):
            ConsoleHandler.cyan()
        elif(colour_char == '7' or colour_char == '9'):
            ConsoleHandler.white()
        else:
            # Do nothing (don't know this code)
            pass

# end MudReadThread class




                   
            