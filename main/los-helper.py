# List of TBDs

#Features
  # ANSI color
  # timed attaking and casting
  #    Stops on MUD output, ie mob dying or spell not exisiting, or trying to move.
  # automatic haste
  # internal timers to eliminate "Please wait 1 seconds."
  # Keeps track of weapon so you can flee.


# idea for a function:
#  MUD_output_check(regex_true, regex_false="regex that won't match", timeout=0.8)
#    checks the MUD_buffer for the regexes
#    returns a match object if regex_true is matched
#    returns null (false) if the regex_false occurs (only purpose is to reduce the amount of time)
#    returns null (false) if the given timeout expires.

# bug... someone else kills my old mob,
# EDIT: I THINK THIS IS FIXED.  I changed the trigger to the 'overwhelms' one
# when a mob is killed so I think this is fine.
# Your enemy, the shepherd had been defeated
# while I'm healing up and stops the combat threads.
#  edit the combat thread stopping logic to compare the kk target to the mob
#  that died.
# FIX:  (two fixes)
#  1.  keep track of which mob you are kk ing and cc ing and only stop
#      kk and cc if the mob that died was your target.
#  2.  engage mobs that attack you.

#bug:
        #Obvious exits: north, south, east.
        #You see a shopper.
        #MUD_READ: successful go
        #Check for successful go, returning True
        #Inside check_for_monsters
        #[52 H 21 M]: The shopper just wandered to the north.
        #Inside decide_which_mob_to_kill
        #Inside engage_monster... engaging shopper
        #[52 H 21 M]: You don't see that here.
        #[52 H 21 M]: Inside get_items
        #Inside check_weapons.
        #Inside engage_mobs_who_joined_in
        #[]
        #Inside heal_up
        #Inside decide_which_mob_to_kill
        #Inside engage_monster... engaging shopper
        #There's nothing here.
        #[52 H 21 M]: You don't see that here.
#FIX ( TBD ):
#  Maintain only ONE monster list.  MUD_thread will generally be
# the only one to add/delete from it.
# The bot will go from this list.
# However if the bot sees a problem, such as "You don't see that here",
# then the bot can remove that mob from the list.  However the MUD thread will
# have to be involved in that anyway.


# haste thread (hc and sh), search thread (searchc and ssearch)
# haste, steel bottles, silver chalices.
# restoratives
# ### Someone just flashed,
# Someone just wandered to the out.  (hidden mobs)
# The 2nd actress blocks your exit.  (bug: attacks the 1st actress)
# remove unneccessary __init__s

# TBD... mages cast faster (change timers)
# TBD... a "set chase" functionality which will automatically chase
#       mobs that run or chase command
# TBD... a "keep item" list, sell all, drop all.
# TBD combat with circle
# TBD reverse engineering ticker timings from Piety and maintain current health
# TBD haste timers and thread.
# TBD implement MAXHP, MAXMP,
# TBD removed prints from selling algorithm, handle multiple grey cloaks
# (add numbers and sell in decreasing order, and not sell 'empty strings if
# could not fit)
# TBD do not crash on empty inventory at tip
# TBD chase monster
# TBD check mob level before engaging... not need mana for low level mobs etc.
#  (smarter decide_whether_to_engage, maybe no MONSTER_KILL_LIST, but
#   better lists to determine difficulty and better intelligence as to whether
#   to engage mobs from each list level based on mana/health)
# TBD when bot starts reinitialize things like MOBS_ATTACKING 




# DONE LIST
# aura checks.
# Bug for kobold guards... won't continue to engage if health is low!
# blocks your exit
#  The 'x' attacks you.
#  You attack the 'x'.
# Debug:
#  1. mobs joining in
#  2. mobs who block
#  3. not fighting in presence of guard . found one bug (re.match)
# "sell silver ring" will a silver chalice...
#  Solution... when doing inventory give everything a good enough name.
#  still needs to avoid all unusable words.  (test: "silver ring", "tiny silver vial")
# "Small mace" -> "small restorative" ... fixed if mace is removed on
#     successful sales... this would be very good to do.
# town guards. Done.  Reworked top level algorithm.
# make flee stop the bot. 

  # Your x breaks and you have to remove it.
# Your x shatters.

# Wearing rings
# Your x falls apart. (armour)
# bug... why does he run by the penitent?

# crits
# You knock the wind out of the x!!
# Your attack knocks the x off balance!!
# The x is caught off guard by your attack!
# Your wind magic buffets the x.

import sys
import getpass
import telnetlib
import threading
from threading import Thread
import atexit 
import re
import time
from misc_functions import *
from Character import *
from BotThread import BotThread
from CommandHandler import CommandHandler
from MudReaderHandler import MudReaderHandler
from MudReaderThread import MudReaderThread
from MudListenerThread import MudListenerThread
from MyBuffer import MyBuffer

character_inst = None
CommandHandler_inst = None
MudReaderThread_inst = None
MudReaderHandler_inst = None

def main():
    global tn
    global character_inst
    global CommandHandler_inst
    global MudReaderThread_inst
    global MudReaderHandler_inst

    tn = connect_to_MUD()  # Sets up telnet object

    character_inst = Character()
    CommandHandler_inst = CommandHandler(character_inst, tn)
    
    magentaprint("creating buffer")
    MUD_buffer = MyBuffer()

    # Thread to listen to telnet socket
    magentaprint("creating listener")
    MudListenerThread_inst = MudListenerThread(tn, MUD_buffer, character_inst)
    MudListenerThread_inst.start()    

    # MudReader: Thread which watches and parses MUD text
    magentaprint("creating reader")
    MudReaderThread_inst = MudReaderThread(MUD_buffer, character_inst, CommandHandler_inst)
    MudReaderThread_inst.start()
    
    # MudReaderHandler: Thread which supplies a couple of 
    # functions in coordinating with the MudReader.  Most 
    # commonly timing related.
    magentaprint("creating handler")
    MudReaderHandler_inst = MudReaderHandler(MudReaderThread_inst, character_inst)

    # Now that the MUD thread is going I can trust it to issue the 
    # username/password prompts
    magentaprint("doing password")
    issue_name_and_password(tn)

    # These threads now belong to the CommandHandler
    # Thread which handles continuous kill function 
    #global user_kk_thread_inst
    #user_kk_thread_inst = None  # Construct later because start() can't take params

    # Thread which handles continuous cast function
    #global user_cc_thread_inst
    #user_cc_thread_inst = None

    global bot_thread_inst
    bot_thread_inst = None

    # Main thread will go to having raw_input open all the time.
    watch_user_input(MudReaderHandler_inst, character_inst)   # The MUD_read thread quits if it hits
                                        # and EOF.  watch_user_input watches for
                                        # that and quits too.

    # Clean exit:  watch_user_input sees the "quit" and sends it, then we
    # get here.  MudReaderThread_inst will quit at the EOF, where we join up.
    
    while (MudReaderThread_inst.is_alive()): 
        MudReaderThread_inst.join(3)  # Wait 3 sec for the other thread to quit.
        if (MudReaderThread_inst.is_alive()):
            MudReaderThread_inst.stop()  # Last resort.

    #Okay, clean exit!  

    tn.close();
    #That's all, folks!



def connect_to_MUD():
    # This function connects to the MUD, returning the telnet object.
    
    HOST = "mud.landsofstone.org"
    PORT = 4801
    tn = telnetlib.Telnet(HOST,PORT)  #No need to call open (http://www.python.org/doc/2.5.2/lib/module-telnetlib.html)

    return tn

def issue_name_and_password(tn):
    
    if(len(sys.argv) >= 3):
        # Use command line arguments for user name and pass
        tn.write(sys.argv[1] + '\n')   # User name
        tn.write(sys.argv[2] + '\n')   # Password
    else:
        # With the MUD thread going already, there is no need to prompt here.
        tn.write(raw_input() + '\n')    # send user name
        password = getpass.getpass("")  # getpass arg is a prompt string;
                                        # empty string means don't prompt
        tn.write(password + '\n')       # send password

    return
    


def watch_user_input(MudReaderHandler_inst, character_inst):
    
    # This thread watches user input.  For now it will shovel everything
    # to the MUD
#    global PREV_USER_COMMAND  # Last command that was typed in.
#    global PREV_COMMAND # Last command that was sent to telnet.
#    global MOVE_CLK
#    global ATTACK_CLK
#    global CAST_CLK
    #global user_kk_thread_inst
    #global user_cc_thread_inst
    global bot_thread_inst
#    global EXPERIENCE
#    global GOLD
#    global MUD_RETURN_ITEM_SOLD
    
    stopping = False;
    while not stopping:
        try:
            user_input = raw_input(); # TBD: This is where the prompt will go (?)
        except EOFError:
            magentaprint("Don't try to crash me!  Use 'quit'.")
            user_input = ""

        # Mass switch on user input to get functionality
        user_input = user_input.lstrip() #Optional
        #PREV_USER_COMMAND = user_input
        if(not MudReaderThread_inst.is_alive()):
            magentaprint("\nWhat happened to read thread?  Time to turf.\n")
            tn.write(user_input + "\n")
            stopping = True
            if(bot_thread_inst != None and bot_thread_inst.is_alive()):
                bot_thread_inst.stop()                
        elif(user_input == "quit"):
            # TBD:  correct if MUD prints "Please wait x more seconds"
            # after quit was sent.
            #PREV_COMMAND=user_input
            tn.write(user_input + "\n")
            stopping = True
            if(bot_thread_inst != None and bot_thread_inst.is_alive()):
                bot_thread_inst.stop()
        elif(re.match("bot ?$|bot [0-9]+$", user_input)):
            #PREV_COMMAND = user_input
            start_bot(user_input, character_inst, CommandHandler_inst) # Code for this at the bottom
        elif(re.match("stop$", user_input)):
            #PREV_COMMAND = user_input
            stop_bot()
        elif(re.match("fle?$|flee$", user_input)):
            stop_bot()
            CommandHandler_inst.process(user_input)  # CommandHandler does 
                                                # everything except the bot.
        else:
            CommandHandler_inst.process(user_input)
        



############################## THE ROBOT ####################################

def start_bot(user_input, character_inst, CommandHandler_inst):
    # No idea how I'm gonna do this.
    # Assume I'm in the chapel.
    # Will need to monitor health... do that first in MUD output.
    # Will need things to be fairly top-down, ie things like go_to_theatre.

    # Maybe a fairly easy approach would be to walk around, and at every step
    # make a list of mobs in the room.  Compare to a list of known mobs and
    # combat the ones we can take.

    # I still want to keep raw_input... so this should be a thread.  Plus
    # its likely good programming practice.

    # Fundamental problem is that all the reading takes place in another
    # thread.  What will happen is I'll start the combat threads and then
    # I will want to wait until the thing is dead, along with other things
    # (likely also act on low health... but later)  I suppose I could have
    # that thread set global flags...  but there has to be a better way!
    # I can only read the telnet object in one place for many reasons.  Should
    # I take it over? It would be really nice to get this bot as one thread!

    # Well... maybe the flag way would be least overhead.  I wouldn't need very
    # many.  Everything that the bot should react to.  Stuff like:
    #   Health (not a flag, just a global... bot can decide when rest)
    #   Mob death
    #   Full health (for resting... however its just like the other health)
    #   Inventory full?  Can probably do without it by selling often.
    #   Mob fleeing.  This is probably necessary because it will happen a lot.
    #       Not right away but I will need a function which can hopefully chase
    #       down mobs... however not so easy because the way back is hard unless
    #       its 100% north/south/east/west.  (way back through door "door" or
    #       "out"?
    #       So its probably fine to have first version of bot not chase
    #       monsters.
    #   Mob attacking you will then happen often - need to react.
    #   Ah here's the big one I have to read for:  Mobs in the room.
    #       It might be worthwhile, every time the bot moves, to stop the
    #       MUD thread and assemble its list itself, then start the MUD
    #       thread again...  might.  The advantage would be that I
    #       know the list is coming.  Can I reliably parse a mob list?
    #           You see a dustman, a mime artist, a sword swallower.
    #           You see a large wallposter.
    #       Not really.  On the other hand it wouldn't hurt to have "large
    #       wallposter" in the list of mobs that I read so long as I never
    #       try to hurt it.
    #   Looking at mobs to see if they are stronger.
    #       That might also be easier if I take over the telnet object briefly.
    #       The problem is that it renders ALL of the text recognition there
    #       unreliable.  Right now all that is there is haste, spellcast checks,
    #       wield checks, and checks to stop stray "kk" threads.  It would be
    #       a real shame to miss a "You feel slower."  I should monitor that
    #       myself.  Could I figure whether something is stronger without
    #       interrupting that thread?  Maybe
    #           tn.write("l\n")
    #           time.sleep(0.5)  # Wait for MUD thread to set a flag
    #           if(mob is weak):  engage.
    #       Messy, messy, messy.
    #       Although, that won't be necessary if I permanently just have a mob
    #       list.  So, leave that as a future project - a bot who can look
    #       at mobs and decide...
    #   Checking equipment
    #       Will probably need a little sleep for this too.  However it isn't
    #       worth the trouble to stop the MUD thread just to do this little
    #       operation.  As much as I hate it I think I'll have to interact
    #       with the other thread.
    # So from that brainstorming it looks like I can do this just by adding
    # to the MUD thread and not having to control it.  Again, I don't really
    # want to stop it because it would make all my actions off text unreliable.
    # Unfortunately my bot will then have lots of sleeps in it... which is really
    # really sucky.  Argh!!  Maybe its better for the bot to have its own access
    # to telnet out!  However that would still have sleeps.  I really want to
    # avoid sleeps.  Maybe I can do whiles and probe global flags.
    #
    # For better or for worse, I'm going to do this with MUD thread still going
    # and I'm going to interact with that thread.

    # Start the bot thread.

    global bot_thread_inst
    global MudReaderHandler_inst

    # Check for an argument
    M_obj = re.search("[0-9]", user_input)
    if (M_obj):
        starting_path = int(M_obj.group(0))
    else:
        starting_path = 0
    
    if (bot_thread_inst != None and bot_thread_inst.is_alive()):
        magentaprint("It's already going, you'll have to stop it.  Use \"stop\".")
    else:
        bot_thread_inst = BotThread(starting_path, character_inst, CommandHandler_inst, MudReaderHandler_inst)
            # Constructor arg is which path to start on.
        bot_thread_inst.start()

    return

def stop_bot():
    global bot_thread_inst
    if (bot_thread_inst != None) and bot_thread_inst.is_alive():
        bot_thread_inst.stop()

    return
    

# All definitions are made, ready to go: call main!!!
# (Maybe rethink program structure later)

#if __name__ == '__main__':
main()
