
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
from MyBuffer import *

class MudReaderThread ( threading.Thread ):
    # This thread watches the the MUD output and appends it 
    # to the buffer for the MudReaderThread to read it.
    
    ConsoleHandler = newConsoleHandler()

    def __init__(self, MUD_buffer_in=None, character_inst=None, CommandHandler_inst=None):
        if MUD_buffer_in == None and character_inst == None and CommandHandler_inst == None:
            return
        Thread.__init__(self)       
        # Constants
        self.ASCII_EOT = 4
        self.ASCII_ESC = 27
        self.ASCII_m = 109
        
        self.MUD_buffer = MUD_buffer_in
        self.character_inst = character_inst
        self.CommandHandler_inst = CommandHandler_inst
            # The MUD output thread needs the CommandHandler in order to stop
            # the combat threads triggered on MUD output.  Epiphany:  it would
            # be better if the combat threads could call a MUD interface object
            # because the relationship now is kind of backwards (the threads are
            # really using the MudHandler and not the other way around.)
        
        self.CHECK_GO_FLAG = False
        self.CHECK_AURA_FLAG = False
        self.CHECK_AURA_SUCCESS = False
        self.CHECK_SELL_FLAG = False
        self.CHECK_INVENTORY_FLAG = False
        
        # Internal Variables
        # variables used for the MUD_output_check function
        # These are used if I decide to implement MUD_output_check
        # which allows you to check for a non-hardcoded regex.
        # No need.
        #self.__check_regex_true = ""
        #self.__check_regex_false = ""
        #self.__check_M_obj = None
        #self.__check_flag = False 
        
        # Two parallel arrays.
        # I believe this to be appropriate for what they are used for.
        # These were used when I wanted to act when a flag was raised.
        # I decided that was too complicated.
        #self.flag_names = ["aura", "go", "inventory", "monster", "sell"]
        #self.request_flags = [False, False, False, False, False]
                            #{"aura":False,
                            #"go":False, 
                            #"inventory":False,
                            #"monster":False,
                            #"sell":False}
            # These flags are set by the MudHandler and notify the 
            # MudReader to look for certain text patterns.  For 
            # example the inventory flag notifies the MudReader to 
            # look for the inventory coming along into the buffer. 
            # Typically a flag is set when something calls one of the 
            # MudHandler functions.
            # order: alphabetical
        
        self.__stopping = False

        atexit.register(self.stop)
    # end __init__
        
    def stop(self):
        self.__stopping = True
    # end stop        
    
    def run(self):
            
        self.__left_off_index = 0  # This is a save point index of the buffer 
                            # so that we know where in the buffer to begin 
                            # printing again.
        currently_escaping = False  # Used to filter escape sequences
        text_buffer = ""
        while(not self.__stopping):
            # This loop will iterate every time something new enters the buffer, 
            # or any of the bot communication flags change
            
            time_loop_start = time.time()
            
            # Do a wait loop.  This means that the main loop will 
            # iterate every time new text comes in.
            # Put in a sleep so the loop doesn't hog too many resources
            timeout = 3
            start_time = time.time()
            run_time = 0
            while(self.__left_off_index == len(self.MUD_buffer.buffer) and
                  run_time < timeout):
                 time.sleep(0.005) 
                 run_time = time.time() - start_time
                
            # Note that that check on the length of the MUD buffer means 
            # that now there's probably new text data.  It doesn't matter 
            # if it timed out, the loop will just iterate with no new data.                 
            
            time_loop_after_waiting = time.time()
                 
            # There seems to be ANSI escape sequence codes which I
            # am going to filter out.  
            # If you are trying to read it, also remember that
            # currently_escaping may remain false over top of a loop
            # iteration.  They're ANSI escape codes (read wikipedia)
                       
            MUD_buffer_copy = self.copy_MUD_buffer()
            new_left_off_index = len(self.MUD_buffer.buffer)            
            
            # First print the new characters.
            unparsed_unprinted_characters_from_server = list(MUD_buffer_copy[self.__left_off_index:len(MUD_buffer_copy)])
            self.__left_off_index = new_left_off_index

            text_out = ""
            num_escape_characters=0
            for c in unparsed_unprinted_characters_from_server:
                if (ord(c) == self.ASCII_EOT):
                    magentaprint("MudReaderThread: Saw the EOT, quitting.")
                    self.stop()
                elif(ord(c) == self.ASCII_ESC):
                    num_escape_characters = num_escape_characters + 1
                    escape_sequence = "" + c
                    currently_escaping = True  
                elif (currently_escaping and ord(c) == self.ASCII_m):
                    num_escape_characters = num_escape_characters + 1
                    escape_sequence = escape_sequence + c
                    currently_escaping = False
                    # Finished an escape sequence... change color.
                    # Print all the stuff in buffer from before the esc
                    # Must be printed here so that the color change occurse 
                    # at the right point.
                    sys.stdout.write(text_out)
                    text_buffer = text_buffer + text_out
                    text_out = ""
                    self.set_colour(escape_sequence);  # Call subroutine to do this.
                elif (currently_escaping):
                    escape_sequence = escape_sequence + c
                    num_escape_characters = num_escape_characters + 1
                else:  #not currently escaping:             
                    text_out = text_out + c
            # Check for some colors.
                    
            # Print to console.
            sys.stdout.write(text_out)   
            # Not using print because
            # it inserts extra spaces.
            
            #sys.stdout.write("/"+out_str)  # puts slashes between text fragments
            sys.stdout.flush()
                                        
            # Debug:  Print ascii out!  (doesn't do every character)
            #for i in range(0, len(out_str)):
            #    sys.stdout.write(str(ord(out_str[i])) + ' ')

            # Store that in a text buffer.  
            text_buffer = text_buffer + text_out
            
            # Unfortunately there are two buffers now, one with and one without 
            # the escape sequences.
            
            # Trim buffers if they are too long.
            L = len(text_buffer)
            if(L >= self.MUD_buffer.size):
                text_buffer = text_buffer[L-self.MUD_buffer.size:L]
            #print "<REPRINT>"+MUD_buffer+"<\REPRINT>"
            
            while(self.MUD_buffer.access_flag == True):
                time.sleep(0.05)
            self.MUD_buffer.access_flag = True
            L = len(self.MUD_buffer.buffer)
            if(L > self.MUD_buffer.size):
                trim_amount = L - self.MUD_buffer.size
                #left_off_index = left_off_index - (L - self.MUD_buffer.buffer.size)
                #self.MUD_buffer.buffer = self.MUD_buffer[L-self.MUD_buffer.size:L]
                self.__left_off_index = self.__left_off_index - trim_amount
                self.MUD_buffer.buffer = self.MUD_buffer.buffer[trim_amount:L]
                #Looks like this is true EVERY TIME
                #magentaprint("Trimmed MUD_buffer: "+str(trim_amount))
                #magentaprint("L is "+str(L))
                #magentaprint("MUD_buffer.size is "+str(self.MUD_buffer.size))
            
            self.MUD_buffer.access_flag = False

            ###### Now match the buffer with some REs  #######
            text_buffer_trunc = 0
            in_combat = (self.CommandHandler_inst.KillThread_inst != None and 
                self.CommandHandler_inst.KillThread_inst.is_alive())

            # INFO screen stuff
            # Note: First instinct was to parse whole screen at once but that doesn't seem necessary now.
            # Nor does it seem necessary to even have a flag with the Bot... but the bot may need that.
            s_numbered = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?"

            M_obj = re.search("     (.+?) the (.+?), a (.+?) of the" + s_numbered + " level    ",text_buffer)
            if(M_obj != None):
                self.character_inst.NAME = M_obj.group(1)
                self.character_inst.RACE = M_obj.group(2)
                self.character_inst.TITLE = M_obj.group(3)
                self.character_inst.LEVEL = re.search("\d+",M_obj.group(4)).group(0)
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                #magentaprint("MudReader got name, race, class, level: %s %s %s %s" % 
                #             (self.character_inst.NAME, self.character_inst.RACE, 
                #              self.character_inst.TITLE, self.character_inst.LEVEL))
                
            M_obj = re.search("Your preferred alignment is (.+?)     ",text_buffer)
            if(M_obj != None):
                self.character_inst.AURA_PREFERRED = M_obj.group(1)
                self.character_inst.AURA_PREFERRED_SCALE = my_list_search(self.character_inst.AURA_LIST, 
                                                                          self.character_inst.AURA_PREFERRED)
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                #magentaprint("MudReader got AURA_PREFERRED and scale: %s %s " % 
                #             (self.character_inst.AURA_PREFERRED, self.character_inst.AURA_PREFERRED_SCALE)) 
                
            #M_obj = re.search("     Sharp   : (\d+) +%  |  |     Earth : (\d+) +%     |",text_buffer)
            #if(M_obj != None):
            #    self.character_inst.WEAPON_SKILLS['Sharp'] = M_obj.group(1)
            #    self.character_inst.MAGIC_SKILLS['Earth'] = M_obj.group(2)
            #    text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            #    magentaprint("MudReader got Sharp and Earth: %s %s " % 
            #                 (self.character_inst.WEAPON_SKILLS['Sharp'], self.character_inst.MAGIC_SKILLS['Earth'])) 
                
                
            M_obj = re.search("You feel yourself moving faster\.",text_buffer)
            if(M_obj != None):
                self.character_inst.HASTING = True
                self.character_inst.ATTACK_WAIT = self.character_inst.ATTACK_PERIOD_HASTE
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("You're already hastened\.",text_buffer)
            #TODO: Its still possible that haste state is invalid.  Here user types
            #haste and I trigger on "You're already hastened"... can by improved by
            #doing everything under covers! (maybe send a command to telnet and use
            #the response to update variables but don't print anything!  This could
            #be a thread.  Or I could cover all the cases that invalidate haste,
            #which is mainly logging in.  TODO: Login_Update() (do with main thread
            #before raw_input call.)
            if(M_obj != None):
                self.character_inst.HASTING = True
                self.character_inst.ATTACK_WAIT = self.character_inst.ATTACK_PERIOD_HASTE
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("You feel slower\.",text_buffer)
            if(M_obj != None):
                self.character_inst.HASTING = False
                self.character_inst.ATTACK_WAIT = self.character_inst.ATTACK_PERIOD
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                
            # Some cast ones.
            # Note: it's important to keep text_buffer_trunc up to date 
            # because we wouldn't want to leave something in the buffer 
            # to the point that cast threads can't be started up!
            M_obj = re.search("That spell does not exist\.", text_buffer)
            if(M_obj):
                # Unset cast wait timer if it turns out no spell was cast
                self.character_inst.CAST_CLK = time.time() - self.character_inst.CAST_WAIT 
                    # reset cast clock
                self.CommandHandler_inst.stop_CastThread()
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("You don't know that spell\.", text_buffer)
            if(M_obj):
                self.character_inst.CAST_CLK = time.time() - self.character_inst.CAST_WAIT 
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("You cannot meet the casting cost!", text_buffer)
            if(M_obj):
                self.character_inst.CAST_CLK = time.time() - self.character_inst.CAST_WAIT 
                    # reset cast clock
                self.CommandHandler_inst.stop_CastThread()
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("Spell name is not unique\.", text_buffer)
            if(M_obj):
                self.character_inst.CAST_CLK = time.time() - self.character_inst.CAST_WAIT 
                    # reset cast clock
                self.CommandHandler_inst.stop_CastThread()
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("Cast what\?", text_buffer)
            if(M_obj):
                self.character_inst.CAST_CLK = time.time() - self.character_inst.CAST_WAIT 
                    # reset cast clock
                self.CommandHandler_inst.stop_CastThread()
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("Your spell fails\.", text_buffer)
            if(M_obj):
                self.character_inst.CAST_CLK = time.time() - self.character_inst.CAST_WAIT
                # BUG
                #  - some spells can be cast again immediately if they fail and some cannot
                #  - equivalently you can move or not move immediately after failing a spell
                #    based on what spell it was.
                #  - Spells that should reset here are vigor, light, show-aura
                #  - spells that should not reset are black magic.  
                    # reset cast clock
                # Do not kill the cast thread if the spell failed  
                if(self.CHECK_AURA_FLAG):
                    self.CHECK_AURA_FLAG=0;
                    self.CHECK_AURA_SUCCESS=0;
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                            
            # Set WEAPON1
            M_obj = re.search("You wield (.*?)\.", text_buffer)
            if (M_obj != None and not re.search(" in your off hand", M_obj.group(1))):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                weap1 = M_obj.group(1)
                # Clip the "a " or the "some "
                if(re.match("a ", weap1)):
                    weap1 = weap1[2:]
                elif(re.match("some ", weap1)):
                    weap1 = weap1[5:]
                self.character_inst.WEAPON1 = weap1
            # Set WEAPON2
            M_obj = re.search("You wield (.*?) in your off hand\.", text_buffer)
            if (M_obj != None):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                weap2 = M_obj.group(1)
                if(re.match("a ",weap2)):
                    weap2 = weap2[2:]
                elif(re.match("some ",weap2)):
                    weap2 = weap2[5:]
                self.character_inst.WEAPON2 = weap2
            
            # The following few are short term.
            # Re equipping weapons if there is a replacement in 
            # inventory (doesn't check for replacement beforehand)
            M_obj = re.search("Your (.*?) breaks and you have to remove it\.", text_buffer)
            if (M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.reequip_weapon(M_obj.group(1))
            M_obj = re.search("Your (.*?) shatters\.", text_buffer)
            if (M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.reequip_weapon(M_obj.group(1))
                
            # Wearing rings
            M_obj = re.search("You get (.+?)\.", text_buffer)
            if (M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                for item in M_obj.group(1).split(','):
                    if(re.search("a (.+?) ring", item)):
                        self.CommandHandler_inst.process("wear ring")
                     
                
                
            # Prompt
            M_obj = re.search("\[(.*?) H (.*?) M\]", text_buffer)
            if (M_obj):
                #magentaprint("MudReader: Got prompt match.")  
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])                
                try:
                    #magentaprint("MudReader: Got health %s mana %s." % (health, mana))
                    self.character_inst.HEALTH = int(M_obj.group(1))
                    self.character_inst.MANA = int(M_obj.group(2))
                except ValueError:
                    # The exception is if there's a glitch in the ANSI code or
                    # character order... happens sometimes.  (Think its the
                    # MUD's fault)  Its not critical, and I don't know how to
                    # recover from it anyway.
                    #magentaprint("MudReader: Got exception.")
                    pass
            # Check if we're dead.
            M_obj = re.search("Obvious exits: amethyst", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                print "Shucks anyhow"
                self.stop()  # breaks program but allows me to see what happened
                    
            # Do some gold stuff.
            # On gold pickup:
            M_obj = re.search("You now have (.+?) gold coins", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.GOLD = int(M_obj.group(1))
            # On tip drop:                    
            M_obj = re.search("You have (.+?) gold\.", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.GOLD = int(M_obj.group(1))
            # On vendor:
            # Also manage the sell check flag (signal to bot)
            M_obj = re.search("The shopkeep gives you (.+?) gold for (an?|some) (.+?)\.", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.GOLD = self.character_inst.GOLD + int(M_obj.group(1))
                self.character_inst.MUD_RETURN_ITEM_SOLD = True
                self.CHECK_SELL_FLAG = 0
                
            # Check the negative cases for the sell check flag.
            M_obj = re.search("The shopkeep won't buy that from you\.", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MUD_RETURN_ITEM_SOLD = False
                self.CHECK_SELL_FLAG = 0
            M_obj = re.search("It isn't empty!", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MUD_RETURN_ITEM_SOLD = False
                self.CHECK_SELL_FLAG = 0
            M_obj = re.search("The shopkeep says, \"I won't buy that rubbish from you\.\"", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MUD_RETURN_ITEM_SOLD = False
                self.CHECK_SELL_FLAG = 0
            M_obj = re.search("Sell what\?", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MUD_RETURN_ITEM_SOLD = False
                self.CHECK_SELL_FLAG = 0

            ########    Do some monster removal.    ######
            
            # Monster is killed
            #M_obj = re.search("Your enemy, the" + s_numbered + " (.+?) has been defeated\.", MUD_buffer)            
            M_obj = re.search("Your attack overwhelms the" + s_numbered + " (.+?) and (s?he|it) collapses!", text_buffer)
            if(M_obj != None):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                if(my_list_search(self.character_inst.MONSTER_LIST, M_obj.group(2)) != -1):
                    magentaprint( "Removing " + M_obj.group(2) + " from MONSTER_LIST")
                    self.character_inst.MONSTER_LIST.remove(M_obj.group(2))
                else:
                    magentaprint("MudReaderThread: Could not remove " + M_obj.group(2) + " from MONSTER_LIST")
                self.CommandHandler_inst.stop_KillThread()
                self.CommandHandler_inst.stop_CastThread()
            # Experience
            M_obj = re.search("You gain (.+?) experience\.", text_buffer)       
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.EXPERIENCE = self.character_inst.EXPERIENCE + int(M_obj.group(1))
            # Monster flees.
            #TODO chasing function.
            M_obj = re.search("The" + s_numbered + " (.+?) flees to the (.+?)\.", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                if(my_list_search(self.character_inst.MONSTER_LIST, M_obj.group(2)) != -1):
                    magentaprint("Removing " + M_obj.group(2) + " from MONSTER_LIST")
                    self.character_inst.MONSTER_LIST.remove(M_obj.group(2))
                else:
                    magentaprint("MudReaderThread: Could not remove " + M_obj.group(2) + " from MONSTER_LIST")
                self.CommandHandler_inst.stop_KillThread()
                self.CommandHandler_inst.stop_CastThread()
            # Stop combat threads on "You don't see that here"
            M_obj = re.search("You don't see that here\.",text_buffer)
            # I don't like PREV_COMMAND.
            # "You don't see that here" needs to terminate kk because
            # MONSTER_LIST can be wrong if a mob arrives at the same time
            # as I leave an area.  So I'm removing prev command and
            # combat will always be stopped on "You don't see that here
            #prev_cmd_kill = re.match("k ",PREV_COMMAND)
            #if(M_obj != None and prev_cmd_kill != None):
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.CommandHandler_inst.stop_KillThread()
                self.character_inst.ATTACK_CLK = time.time()-self.character_inst.ATTACK_WAIT
                        #unset attack timer which would prevent action.
            M_obj = re.search("They are not here\.", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.CommandHandler_inst.stop_CastThread()
                self.character_inst.CAST_cLK = time.time() - self.character_inst.CAST_WAIT
                               
            # Monster wanders to specific exit
            M_obj = re.search("The" + s_numbered + " (.+?) just wandered to the .+?\.", text_buffer)
            if(M_obj):
                magentaprint( "Matched " + M_obj.group(2))
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                if(my_list_search(self.character_inst.MONSTER_LIST, M_obj.group(2)) != -1):
                    self.character_inst.MONSTER_LIST.remove(M_obj.group(2))
                else:
                    magentaprint("MudReaderThread: Could not remove " + M_obj.group(2) + " from MONSTER_LIST")
            # Monster wanders away
            M_obj = re.search("The" + s_numbered + " (.+?) just wandered away\.", text_buffer)
            if(M_obj):
                magentaprint( "Matched " + M_obj.group(2))
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                if(my_list_search(self.character_inst.MONSTER_LIST, M_obj.group(2)) != -1):
                    self.character_inst.MONSTER_LIST.remove(M_obj.group(2))
                else:
                    magentaprint("MudReaderThread: Could not remove " + M_obj.group(2) + " from MONSTER_LIST")
            # Monster arrival
            M_obj = re.search("An? (.+?) just arrived\.", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MONSTER_LIST.append(M_obj.group(1))
            # Monsters joining in
            # Two strings which can occur
            # This one is for when a mob that is present starts fighting
            # Note that the following is safe if two strings occur 
            # simultaneously!
            #  Aside:  Maybe more of the matches should work this way.
            #  However I'm hoping to move away from read_very_eager so 
            #  that task is pending.
            join_in_regex = "the" + s_numbered + " (.+?) joins in the fight!"
            M_obj = re.search(join_in_regex, text_buffer)
            new_trunc = 0
            temp_buf = text_buffer[:] # copy
            # Need to check for multiple matches here.
            while(M_obj):
                new_trunc = new_trunc + M_obj.end()
                text_buffer_trunc = max([text_buffer_trunc, new_trunc])
                self.character_inst.MOBS_JOINED_IN.append(M_obj.group(2))
                    # Note... this thread just appends... let the bot
                    # remove stuff.  I can't differentiate between 
                    # any mob and one that joined in!
                    # I will only remove from MONSTER_LIST
                temp_buf = temp_buf[new_trunc:]
                M_obj = re.search(join_in_regex, temp_buf)
                
            # This other string occurs when a mob wanders in and joins the fight    
            second_join_in_regex = "the" + s_numbered + " (.+?) decides to join in on the fight!"
            M_obj = re.search(second_join_in_regex, text_buffer)
            new_trunc = 0
            temp_buf = text_buffer[:] # copy
            while(M_obj):
                new_trunc = new_trunc + M_obj.end()
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MOBS_JOINED_IN.append(M_obj.group(2))
                temp_buf = temp_buf[new_trunc:]
                M_obj = re.search(second_join_in_regex, temp_buf)
                
            # Mobs Attacking you (not from joining in)
            
            mobs_attacking_regexes = [
                "The" + s_numbered + " (.+?) punches you for (.+?) damage\.",
                "The" + s_numbered + " (.+?) throws a wild punch at you, but it misses\.",
                "The" + s_numbered + " (.+?) kicks you for (.+?) damage\.",
                "The" + s_numbered + " (.+?) kicks at you, but fails to hurt you\.",
                "The" + s_numbered + " (.+?) grabs you and gouges you for (.+?) damage\.",
                "The" + s_numbered + " (.+?) tries to grab you, but you break free of (his|her|its) grasp\.",
                "The" + s_numbered + " (.+?) tries to gouge you, but you shake (him|her|it) off\.",
                "The" + s_numbered + " (.+?) lashes out and thumps you for (.+?) damage\.",
                "The" + s_numbered + " (.+?) lashes out at you, but misses\.",               
                "The" + s_numbered + " (.+?) painfully head-butts you for (.+?) damage\.",
                "The" + s_numbered + " (.+?) casts a (.+?) on you for (.+?) damage\.",
                "The" + s_numbered + " (.+?) casts a (.+?) at you for (.+?) damage\."] #not sure if its 'on' or 'at'
                # Thought:  We know a mob is attacking also on strings where I attack it, 
                # but it's doubtfully necessary to add that mob to MOBS_ATTACKING.
            for attacking_regex in mobs_attacking_regexes:
                # I think it would be difficult to determine here how many of a certain mob are 
                # attacking so just make sure that there's one instance of the attacking mob 
                # in ATTACKING_MOBS
                M_obj = re.search(attacking_regex, text_buffer)
                if(M_obj):
                    text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                    if(my_list_search(self.character_inst.MOBS_ATTACKING, M_obj.group(2)) == -1):
                        self.character_inst.MOBS_ATTACKING.append(M_obj.group(2))    
                
            # Bot wants to know what monsters are present.
            # Assume he already typed look.
            
            # Following regex:
            #  - conclude successful go
            #  - Empty MONSTER_LIST
            # Note that if there are items present but no monsters
            # I can't detect it and the bot will just have to time out
            # or something.
            M_obj = re.search("Obvious exits: .+?\.\n\r\n\r", text_buffer)
            if(M_obj):
                #magentaprint("MudReader: No monsters present, unsetting MONSTER_CHECK_FLAG")
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MONSTER_LIST = []
                self.character_inst.SUCCESSFUL_GO = True
                self.CHECK_GO_FLAG = 0
            # Following regex:  If we see it we can
            #  - conclude successful go
            #  - populate MONSTER_LIST
            M_obj = re.search("(?s)Obvious exits: .+?\.\n\r(You see .+?\.)", text_buffer)  # Match multlines
            # Note.  If there are no monsters but there are items this will also match!
            # There's no way to determine that.  However, it's not important 
            # because the bot will never try to engage and item :)                    
            if(M_obj != None):
                #magentaprint("MudReader: Monsters are seen, need to parse, then unset flag.")
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MONSTER_LIST = self.parse_monster_list(M_obj.group(1))
                self.character_inst.SUCCESSFUL_GO = True
                self.CHECK_GO_FLAG = 0
            # On too dark:
            #    - conclude successful go
            #    - leave MONSTER_LIST empty
            M_obj = re.search("It's too dark to see\.", text_buffer)
            if(M_obj):
                #magentaprint("MudReader: Too dark, unsetting MONSTER_CHECK_FLAG")
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.MONSTER_LIST = []
                self.character_inst.SUCCESSFUL_GO = True
                self.CHECK_GO_FLAG = 0
            # Mob blocking exit:
            #    - unsuccessful go
            #    - don't touch MONSTER_LIST 
            # Note:  Previous versions insisted that I don't clear the buffer 
            # here.  That is because it used to be two separate operations to 
            # check for successful go and populate the monster list.  That's 
            # one of the motivations for revamping.  Now I am doing both 
            # simultaneously because they use the same text.  So now I want it 
            # cleared.
            M_obj = re.search("The" + s_numbered + " (.+?) blocks your exit\.", text_buffer)
            if(M_obj):
                #magentaprint("MudReader: unsuccessful go %f" % (time.time()-self.character_inst.START_TIME))
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.GO_BLOCKING_MOB = M_obj.group(2)  
                self.character_inst.SUCCESSFUL_GO = False
                self.CHECK_GO_FLAG = 0
            M_obj = re.search("Please wait 1 more second\.", text_buffer)
            if(M_obj):
                #magentaprint("MudReader: unsuccessful go (please wait)")
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.GO_PLEASE_WAIT = True
                self.character_inst.SUCCESSFUL_GO = False
                self.CHECK_GO_FLAG = 0
            M_obj = re.search("You can't go that way\.", text_buffer)
            if(M_obj):
                # This one is pretty problematic... as it should never happen.
                # Means we're off course.
                #magentaprint("MudReader: unsuccessful go (you can't go that way)")
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.GO_NO_EXIT = True
                self.character_inst.SUCCESSFUL_GO = False
                self.CHECK_GO_FLAG = 0
            M_obj = re.search("I don't see that exit\.", text_buffer)
            if(M_obj):
                #magentaprint("MudReader: unsuccessful go (you can't go that way)")
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.GO_NO_EXIT = True
                self.character_inst.SUCCESSFUL_GO = False
                self.CHECK_GO_FLAG = 0

            # Aura
            M_obj = re.search("You glow with an? (.+?) aura\.", text_buffer)
            # Interestingly the MUD never says 'an' here.  Leave the '?' in though.
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.AURA = M_obj.group(1)
                self.character_inst.AURA_SCALE = my_list_search(self.character_inst.AURA_LIST, self.character_inst.AURA)
                if(self.character_inst.AURA_SCALE == -1):
                    magentaprint('Error in reading aura (not in list), came out as ' + self.character_inst.AURA + '.')
                self.CHECK_AURA_FLAG = 0
                self.CHECK_AURA_SUCCESS = 1
        
            # Having red aura in chapel.
            # The bot should definitely leave in this case.
            # However I only want to leave if the bot is currently going...
            # Ohwell.  This might inconvenience a human user but I'm putting it in.
            M_obj = re.search("The goodness here sickens and repels you!", text_buffer)
            if(M_obj):
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.CommandHandler_inst.process("ou")
            
            # Inventory
            M_obj = re.search("(?s)You have: (.+?)\.", text_buffer)
            if(M_obj):
                #magentaprint("MudReaderThread: Got inventory list.  Parsing now.")
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character_inst.INVENTORY_LIST = self.parse_inventory_list(M_obj.group(1))
                self.CHECK_INVENTORY_FLAG = 0  
        
            # Internal check function MUD_output_check
            #if(self.__check_flag):
            #    M_obj = re.search(self.__check_regex_true, text_buffer)
            #    if(M_obj):
            #        self.__check_M_obj = M_obj
            #        self.__check_flag = False
            #    M_obj = re.search(self.__check_regex_false, text_buffer)
            #    if(M_obj):
            #        self.__check_M_obj = None
            #        self.__check_flag = False
            ##### DONE MATCHING RE's  WOOOOOOOO ######
        
            #sys.stdout.write('"' + MUD_buffer[MUD_buffer_trunc] + '"') #debug.  Shows where last match took place. Gives MUD_buffer not defined error.
            #magentaprint("Clearing text buffer.  len: %d.  trunc: %d.  last matched char: %c." % (
            #           len(text_buffer), text_buffer_trunc, text_buffer[text_buffer_trunc]))
            text_buffer = text_buffer[text_buffer_trunc:]
        
            #magentaprint("MudReader loop times: incl wait: %f; iteration time: %f" % 
            #             (time.time()-time_loop_start, time.time()-time_loop_after_waiting))
        # end loop          

    # end run  (congrats!)

    def copy_MUD_buffer(self):
        
        # Routine to copy the buffer shared with MudListenerThread.
        # Wait for access flag to go down for the read.
        while(self.MUD_buffer.access_flag == True):
            time.sleep(0.05)
            
        self.MUD_buffer.access_flag = True
        MUD_buffer_copy = self.MUD_buffer.buffer[:]
        self.MUD_buffer.access_flag = False
        return MUD_buffer_copy

    def set_colour(self,ANSI_escape_sequence):
        """ This routine takes an ANSI escape sequence as an argument and
        calls the ConsoleHandler class routines to have the windows console react."""
        bright_char = ANSI_escape_sequence[2]
        colour_char = ANSI_escape_sequence[3]
        if(bright_char == '3'):
            self.ConsoleHandler.set_dark()
        elif(bright_char == '4'):
            self.ConsoleHandler.set_bright()
        else:
            pass # do nothing
        # Maybe check if character 2 is a '3' or '4' which designate colour
        # commands but I'm too lazy.
        if(colour_char == '0'):
            self.ConsoleHandler.black()
        elif(colour_char == '1'):
            self.ConsoleHandler.red()
        elif(colour_char == '2'):
            self.ConsoleHandler.green()
        elif(colour_char == '3'):
            self.ConsoleHandler.yellow()
        elif(colour_char == '4'):
            self.ConsoleHandler.blue()
        elif(colour_char == '5'):
            self.ConsoleHandler.magenta()
        elif(colour_char == '6'):
            self.ConsoleHandler.cyan()
        elif(colour_char == '7' or colour_char == '9'):
            self.ConsoleHandler.white()
        else:
            # Do nothing (don't know this ANSI code)
            pass
                
    
    def parse_monster_list(self, MUD_mob_str):
        """ This function takes a LOS formatted string list of monsters such as:
                'You see an acolyte, an amethyst town crier, two kobold children.'
            and returns a parsed list such as
                ['acolyte', 'amethyst town crier', 'kobold child', 'kobold child']
        """
        # TODO:  This would be a lot less painful with split!!!
        # Good target for the rewrite train!
        # Also it used to be in two functions in different files.
        # Now it's one :)

        #print "Got a match!"
        num_commas = MUD_mob_str.count(',')
        #print "num_commas" + str(num_commas)
        num_monsters = num_commas + 1
        # Take out \n's and \r's
        #print MUD_mob_str
        MUD_mob_str = self.replace_newlines_with_spaces(MUD_mob_str)
        my_monster_regex = "You see "
        for i in range(1,num_commas+1):
            # Add a regex group for each mob, and nab the comma
            # and space afterwards too.
            my_monster_regex = my_monster_regex + "(.+?), "
        my_monster_regex = my_monster_regex + "(.+?)\."
        #print "my_monster_regex: " + my_monster_regex
        match_monsters = re.match(my_monster_regex, MUD_mob_str)

        M_LIST = []
        for i in range(1, num_monsters+1):
            M_LIST.append(match_monsters.group(i))

        # Trim the preceding "a" or "some" or "two," s well as the
        # trailing comma, and the 's' if it was plural and there's an 's'
        for i in range(0, len(M_LIST)):
            #M_LIST[i].ljust(0)  # this isn't doing what I thought.
            M_LIST[i].lstrip()  # remove the space.
            if (re.match("a ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][2:]
            elif (re.match("an ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][3:]
            elif (re.match("two ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][4:]
                if (M_LIST[i][len(M_LIST[i]) - 3:] == "ses"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 2]
                elif (M_LIST[i][len(M_LIST[i]) - 1] == 's'):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 1]
                elif (M_LIST[i][len(M_LIST[i]) - 8:] == "children"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 3]
                M_LIST.append(M_LIST[i])
            elif (re.match("three ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][6:]
                if (M_LIST[i][len(M_LIST[i]) - 3:] == "ses"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 2]
                elif (M_LIST[i][len(M_LIST[i]) - 1] == 's'):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 1]
                elif (M_LIST[i][len(M_LIST[i]) - 8:] == "children"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 3]
                for j in range(1, 3):
                    M_LIST.append(M_LIST[i])
            elif (re.match("four ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][5:]
                if (M_LIST[i][len(M_LIST[i]) - 3:] == "ses"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 2]
                elif (M_LIST[i][len(M_LIST[i]) - 1] == 's'):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 1]
                elif (M_LIST[i][len(M_LIST[i]) - 8:] == "children"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 3]
                for j in range(1, 4):
                    M_LIST.append(M_LIST[i])
            commaindex = M_LIST[i].find(',')
            if (commaindex != -1):
                M_LIST = M_LIST[:commaindex]
        return M_LIST
    
    def replace_newlines_with_spaces(self, s):
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
    
    def parse_inventory_list(self, inv_string):
        # Now match it.  Have to do the same as MONSTER_LIST
        # where I count commas...
        # I won't have to worry about You have: if I take the group
        # already obtained in M_obj... actually I might even be able
        # to get off really easy with a split!!
        return_list = []
        # Replace newlines with spaces
        inv_string = self.replace_newlines_with_spaces(inv_string)
        # Use split to break into a list of strings
        #print inv_string
        inv_list = inv_string.split(',')
        #print inv_list
        for i in range(0, len(inv_list)):
            inv_list[i] = inv_list[i].lstrip()
            inv_list[i] = inv_list[i].rstrip()
            #print inv_list[i]
            #print i
            #sys.stdout.write("Appending... ")
            # How should I do quantities?  It probably makes sense
            # just to have duplicate items in the actual list
            if(inv_list[i][0:2] == "a "):
                inv_list[i] = inv_list[i][2:]
                return_list.append(inv_list[i])
                #sys.stdout.write(inv_list[i] + '\n')
            elif(inv_list[i][0:3] == "an "):
                inv_list[i] = inv_list[i][3:]
                return_list.append(inv_list[i])
                #sys.stdout.write(inv_list[i] + '\n')
            elif(inv_list[i][0:5] == "some "):
                inv_list[i] = inv_list[i][5:]
                return_list.append(inv_list[i])
                #sys.stdout.write(inv_list[i] + '\n')
            # In doing quantities, may as well use insert and keep
            # the list ordered.
            elif(inv_list[i][0:4] == "two "):
                #sys.stdout.write("   In two...   ")
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
                    return_list.append(inv_list[i])
                #sys.stdout.write(str(inv_list[i]) + '\n')
                #inv_list.insert(i, inv_list[i]) # check this
            elif(inv_list[i][0:6] == "three "):
                #sys.stdout.write("   In three...   ")
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
                    return_list.append(inv_list[i])
                #sys.stdout.write(str(inv_list[i]) + '\n')
            elif(inv_list[i][0:5] == "four "):
                #sys.stdout.write("   In four...   ")
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
                    return_list.append(inv_list[i])
                #sys.stdout.write(str(inv_list[i]) + "\n")
            elif(inv_list[i][0:5] == "five "):
                #sys.stdout.write("   In five...   ")
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
                    return_list.append(inv_list[i])
                #sys.stdout.write(str(inv_list[i]) + '\n')
            # TODO go up to fifteen.  Maybe find a more scalable way to
            # do it.
            else:
                #print "BIG FAT ELSE"
                pass

        return return_list
    
    
    def reequip_weapon(self, weapon_str):
        if(self.character_inst.WEAPON1 == self.character_inst.WEAPON2):
            # If weap 1 and weap 2 are the same, not sure how to know 
            # which broke... so just put in both commands :)
            self.CommandHandler_inst.process("wie " + weapon_str)
            self.CommandHandler_inst.process("seco " + weapon_str)
        else:
            if(weapon_str == self.character_inst.WEAPON1):
                self.CommandHandler_inst.process("wie " + weapon_str)
            else:
                self.CommandHandler_inst.process("seco " + weapon_str)
        
    

# end MudReaderThread class


