
import threading
from threading import Thread
import atexit 
import time
import re
import sys
import select

from misc_functions import *

class MudReaderThread(threading.Thread):
    """This thread watches the the MUD output and appends it
    to the buffer for the MudReaderThread to read it."""
    
    def __init__(self, MUDBuffer, character, consoleHander):
        Thread.__init__(self)       
        # Constants
        self.ASCII_EOT = 4
        self.ASCII_ESC = 27
        self.ASCII_m = 109
        
        self.MUDBuffer = MUDBuffer
        self.character = character
        self.consoleHander = consoleHander
        
        #TODO: change these all to mud waiter flags
        self.CHECK_GO_FLAG = False
        self.CHECK_SELL_FLAG = False
        self.CHECK_INVENTORY_FLAG = False
        #self.CHECK_KILL_MONSTER_GONE = False # This one isn't used yet, I think it's to react to when a monster flees
        
        self.BotReactionList = []
        self.mud_events = {}

        self.recording = False
        self.recorded_text = ''
        
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
            # ... the better pattern is for the MudReader (observer) to 
            # always match the pattern and let things subscribe to notifications.
        
        self.stopping = False
        atexit.register(self.stop)
                
    def stop(self):
        self.stopping = True
    
    def run(self):
        self.__left_off_index = 0  # This is a save point index of the buffer
                            # so that we know where in the buffer to begin
                            # printing again.
        currently_escaping = False  # Used to filter escape sequences
        text_buffer = ""
        while not self.stopping:
            time_loop_start = time.time()

            # Do a wait loop.  This means that the main loop will
            # iterate every time new text comes in.
            # Put in a sleep so the loop doesn't hog too many resources
            # (I think MudListener should call some sort of notify...)
            timeout = 1
            start_time = time.time()
            run_time = 0

            while self.__left_off_index == len(self.MUDBuffer.buffer) and run_time < timeout:
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

            MUDBuffer_copy = self.copy_MUDBuffer()
            new_left_off_index = len(self.MUDBuffer.buffer)

            # First print the new characters.
            unparsed_unprinted_characters_from_server = list(MUDBuffer_copy[self.__left_off_index:len(MUDBuffer_copy)])
            self.__left_off_index = new_left_off_index

            text_out = ""
            num_escape_characters=0
            for c in unparsed_unprinted_characters_from_server:
                if ord(c) == self.ASCII_EOT:
                    magentaprint("MudReaderThread: Saw the EOT, quitting.")
                    self.stop()
                elif ord(c) == self.ASCII_ESC:
                    num_escape_characters = num_escape_characters + 1
                    escape_sequence = "" + c
                    currently_escaping = True
                elif currently_escaping and ord(c) == self.ASCII_m:
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
                elif currently_escaping:
                    escape_sequence = escape_sequence + c
                    num_escape_characters = num_escape_characters + 1
                else:  #not currently escaping:
                    text_out = text_out + c
            # Check for some colors.

            sys.stdout.write(text_out)

            # Not using print because it inserts extra spaces.

            #sys.stdout.write("/"+out_str)  # puts slashes between text fragments for debugging
            sys.stdout.flush()

            if self.recording:
                self.recorded_text +=  text_out

            # Debug:  Print ascii out!  (doesn't do every character)
            #for i in range(0, len(out_str)):
            #    sys.stdout.write(str(ord(out_str[i])) + ' ')

            # Store that in a text buffer.  
            text_buffer = text_buffer + text_out

            # Unfortunately there are two buffers now, one with and one without 
            # the escape sequences.

            # Trim buffers if they are too long.
            L = len(text_buffer)
            if(L >= self.MUDBuffer.size):
                text_buffer = text_buffer[L-self.MUDBuffer.size:L]
            #print "<REPRINT>"+MUD_buffer+"<\REPRINT>"

            while(self.MUDBuffer.access_flag == True):
                time.sleep(0.05)

            self.MUDBuffer.access_flag = True
            L = len(self.MUDBuffer.buffer)

            if(L > self.MUDBuffer.size):
                trim_amount = L - self.MUDBuffer.size
                self.__left_off_index = self.__left_off_index - trim_amount
                self.MUDBuffer.buffer = self.MUDBuffer.buffer[trim_amount:L]
                #magentaprint("Trimmed MUDBuffer: "+str(trim_amount))
                #magentaprint("L is "+str(L))
                #magentaprint("MUDBuffer.size is "+str(self.MUDBuffer.size))

            self.MUDBuffer.access_flag = False

            ###### Now match the buffer with some REs  #######
            text_buffer_trunc = 0

            # MudEvents
            # Regexes with lists of objects to notify.
            for key, m in self.mud_events.items():
                for r in m.regexes:
                    M_obj = re.search(r, text_buffer)
                    if M_obj is not None:
                        for s in m.subscribers:
                            s.notify(r, M_obj)
                        m.notify()
                        text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                        # import RegexStore
                        # if r in RegexStore.haste_fail or r in RegexStore.hastened or r in RegexStore.already_hastened:
                        #     magentaprint("MudReaderThread: " + str(r))

            # Bot Reactions
            # TODO: create a flag that stops other threads from writing the list
            # while I'm in here.  (could cause a missed reaction)
            reactions_to_delete = []
            for reaction in self.BotReactionList:
                if reaction.unregistered:
                    reactions_to_delete.append(reaction)
                    continue
                # magentaprint(reaction.regexes)
                # magentaprint(reaction)
                for regex in reaction.regexes:
                    # magentaprint("Regex: " + str(regex))
                    try:
                        M_obj = re.search(regex, text_buffer)
                    except TypeError:
                        magentaprint("MudReaderThread reaction TypeError: " + str(reaction.__class__) + " regex: " + str(regex))

                    # if(M_obj != None):
                    if M_obj:
                        # magentaprint("MudReaderThread: calling notify on " + str(reaction))
                        reaction.notify(regex, M_obj)
                        text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])

            # reaction_counter = 0  # TODO: delete reaction_counter and all reaction printing
            for reaction in reactions_to_delete:
                try:
                    self.BotReactionList.remove(reaction)
                    # magentaprint(str(len(self.BotReactionList)) + " reactions.")
                except ValueError:
                    magentaprint("MudReaderHandler could not unregister reaction!")
                    magentaprint("Reaction: " + str(reaction))
                    magentaprint("ReactionList: " + str(self.BotReactionList))
                    magentaprint("Reaction regexes: " + str(reaction.regexes))
                # else:
                #     magentaprint("Removed a reaction.")

                # reaction_counter = reaction_counter + 1

            # if reaction_counter > 0:
            #     magentaprint(str(len(self.BotReactionList) + " reactions, deleted " + str(reaction_counter)))
            #     magentaprint("MudReaderThread removed " + str(reaction_counter) + 
            #                  " reactions," + str(len(self.BotReactionList)) + 
            #                  " reactions left.")

            #TODO: continue with MAXHP, MAXMP, GOLD, EXP, LEVELGOLD, LEVELEXP, etc.
            M_obj = re.search("Exp : (\d+)",text_buffer)
            if (M_obj != None):
                self.character.TOTAL_EXPERIENCE = M_obj.group(1)

            M_obj = re.search("Gold : (\d+)",text_buffer)
            if (M_obj != None):
                self.character.TOTAL_GOLD = M_obj.group(1)

            #### Set weapon strings ####
            # M_obj = re.search("You wield (.*?)\.", text_buffer)
            # if (M_obj != None and not re.search(" in your off hand", M_obj.group(1))):
            #     text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            #     weap1 = M_obj.group(1)
            #     # Clip the "a " or the "some "
            #     if(re.match("a ", weap1)):
            #         weap1 = weap1[2:]
            #     elif(re.match("some ", weap1)):
            #         weap1 = weap1[5:]
            #     self.character.weapon1 = weap1
            # M_obj = re.search("You wield (.*?) in your off hand\.", text_buffer)
            # if (M_obj != None):
            #     text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            #     weap2 = M_obj.group(1)
            #     if(re.match("a ",weap2)):
            #         weap2 = weap2[2:]
            #     elif(re.match("some ",weap2)):
            #         weap2 = weap2[5:]
            #     self.character.weapon2 = weap2

            #### Shopping stuff ####
            # On gold pickup:
            M_obj = re.search("You now have (.+?) gold coins", text_buffer)
            if(M_obj):
                self.character.GOLD = int(M_obj.group(1))
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            # On tip drop:                    
            M_obj = re.search("You have (.+?) gold\.", text_buffer)
            if(M_obj):
                self.character.GOLD = int(M_obj.group(1))
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])

            # On vendor ... also manage the sell check flag (signal to bot)
            M_obj = re.search("The shopkeep gives you (.+?) gold for (an?|some) (.+?)\.", text_buffer)
            if(M_obj):
                self.character.GOLD = self.character.GOLD + int(M_obj.group(1))
                self.character.MUD_RETURN_ITEM_SOLD = True
                self.CHECK_SELL_FLAG = 0
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("The shopkeep won't buy that from you\.", text_buffer)
            if(M_obj):
                self.character.MUD_RETURN_ITEM_SOLD = False
                self.CHECK_SELL_FLAG = 0
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("It isn't empty!", text_buffer)
            if(M_obj):
                self.character.MUD_RETURN_ITEM_SOLD = False
                self.CHECK_SELL_FLAG = 0
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("The shopkeep says, \"I won't buy that rubbish from you\.\"", text_buffer)
            if(M_obj):
                self.character.MUD_RETURN_ITEM_SOLD = False
                self.CHECK_SELL_FLAG = 0
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            M_obj = re.search("Sell what\?", text_buffer)
            if(M_obj):
                self.character.MUD_RETURN_ITEM_SOLD = False
                self.CHECK_SELL_FLAG = 0
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])

            #### Check if we're dead ####
            M_obj = re.search("You are overwhelmed by (.+?)'s attack and you collapse!", text_buffer)
            if M_obj:
                magentaprint("Shucks anyhow")
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
                self.character.DEAD = True
                # self.stop()  # breaks program but allows me to see what happened

            ########    Monster Gets Killed    ######
            s_numbered = "( \d+?1st| \d+?2nd| \d+?3rd| \d+th)?"

            # Experience
            M_obj = re.search("You gain (.+?) experience\.", text_buffer)       
            if(M_obj):
                self.character.EXPERIENCE = self.character.EXPERIENCE + int(M_obj.group(1))
                text_buffer_trunc = max([text_buffer_trunc, M_obj.end()])
            # Monster flees.
            #TODO chasing function.

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
                self.character.MOBS_JOINED_IN.append(M_obj.group(2))
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
                self.character.MOBS_JOINED_IN.append(M_obj.group(2))
                temp_buf = temp_buf[new_trunc:]
                M_obj = re.search(second_join_in_regex, temp_buf)

            # Quitting... instead have the caller call stop.
            # M_obj = re.search("Goodbye! Come back soon\.", text_buffer)
            # if M_obj:

            ##### DONE MATCHING RE's  WOOOOOOOO ######

            #sys.stdout.write('"' + MUDBuffer[MUD_buffer_trunc] + '"') #debug.  Shows where last match took place. Gives MUD_buffer not defined error.
            #magentaprint("Clearing text buffer.  len: %d.  trunc: %d.  last matched char: %c." % (
            #           len(text_buffer), text_buffer_trunc, text_buffer[text_buffer_trunc]))
            text_buffer = text_buffer[text_buffer_trunc:]

            #magentaprint("MudReader loop times: incl wait: %f; iteration time: %f" % 
            #             (time.time()-time_loop_start, time.time()-time_loop_after_waiting))
        # end loop          
    # end run  (congrats!)

    def copy_MUDBuffer(self):

        # Routine to copy the buffer shared with MudListenerThread.
        # Wait for access flag to go down for the read.
        while(self.MUDBuffer.access_flag == True):
            time.sleep(0.05)

        self.MUDBuffer.access_flag = True
        MUDBuffer_copy = self.MUDBuffer.buffer[:]
        self.MUDBuffer.access_flag = False
        return MUDBuffer_copy

    def set_colour(self,ANSI_escape_sequence):
        """ This routine takes an ANSI escape sequence as an argument and
        calls the ConsoleHandler class routines to have the windows console react."""
        bright_char = ANSI_escape_sequence[2]
        colour_char = ANSI_escape_sequence[3]
        if(bright_char == '3'):
            self.consoleHander.set_dark()
        elif(bright_char == '4'):
            self.consoleHander.set_bright()
        else:
            pass # do nothing
        # Maybe check if character 2 is a '3' or '4' which designate colour
        # commands but I'm too lazy.
        if(colour_char == '0'):
            self.consoleHander.black()
        elif(colour_char == '1'):
            self.consoleHander.red()
        elif(colour_char == '2'):
            self.consoleHander.green()
        elif(colour_char == '3'):
            self.consoleHander.yellow()
        elif(colour_char == '4'):
            self.consoleHander.blue()
        elif(colour_char == '5'):
            self.consoleHander.magenta()
        elif(colour_char == '6'):
            self.consoleHander.cyan()
        elif(colour_char == '7' or colour_char == '9'):
            self.consoleHander.white()
        else:
            # Do nothing (don't know this ANSI code)
            pass

    def start_recording_mud_text(self):
        self.recording = True

    def stop_recording_mud_text(self):
        self.recording = False
