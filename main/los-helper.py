
# Top of los-helper file is currently used as a note pad for
# FEATURES
# DONE LIST
# TODO LIST
# CODING IDEAS
# STRINGS to save and match later

##########################################################################

# FEATURES available to user not using bot itself

#   timed attaking and casting (kk and cc commands)
#       These commands will continue until certain MUD output including 
#           mob being killed 
#           spell not known 
#           if you move to a new area
#   timed attacking includes change to hasted attack timing 
#   internal timers to eliminate "Please wait 1 second."
#   Keeps track of weapon so you can flee.
#   Guaranteed-to-work flee function available to user and keeps weapon(s). 
#       command is "fl"
#       will wait the exact right amount of time if you cannot yet flee
#       spams flee command 3 times to ensure you get out :)
#   Bot can be used to do selling and dropping at tip (put items you want to 
#       keep that aren't in KEEP_LIST into some bag that IS in KEEP_LIST)
#   ANSI color

##########################################################################

# DONE LIST
# (copy text here when removed from todo list)
#
# aura checks.
#
# Bug for kobold guards... won't continue to engage if health is low!
# blocks your exit
#  The 'x' attacks you.
#  You attack the 'x'.
# Debug:
#  1. mobs joining in
#  2. mobs who block
#  3. not fighting in presence of guard . found one bug (re.match)
#
# "sell silver ring" will sell a silver chalice...
#  Solution... when doing inventory give everything a good enough name.
#  still needs to avoid all unusable words.  (test: "silver ring", "tiny silver vial")
# "Small mace" -> "small restorative" ... fixed if mace is removed on
#     successful sales... this would be very good to do.
#
# town guards. Done.  Reworked top level algorithm.
#
# make flee stop the bot. 
#
# Bot equips weapon on these triggers
# Your x breaks and you have to remove it.
# Your x shatters.
#
# Wearing rings
# Your x falls apart. (armour)
#
#  Maintain only ONE monster list.  MUD_thread will generally be
# the only one to add/delete from it. DONE
# The bot will go from this list.
# However if the bot sees a problem, such as "You don't see that here",
# then the bot can remove that mob from the list.  However the MUD thread will
# have to be involved in that anyway.
#  Example bug:
#        #Obvious exits: north, south, east.
#        #You see a shopper.
#        #MUD_READ: successful go
#        #Check for successful go, returning True
#        #Inside check_for_monsters
#        #[52 H 21 M]: The shopper just wandered to the north.
#        #Inside decide_which_mob_to_kill
#        #Inside engage_monster... engaging shopper
#        #[52 H 21 M]: You don't see that here.
#        #[52 H 21 M]: Inside get_items
#        #Inside check_weapons.
#        #Inside engage_mobs_who_joined_in
#        #[]
#        #Inside heal_up
#        #Inside decide_which_mob_to_kill
#        #Inside engage_monster... engaging shopper
#        #There's nothing here.
#        #[52 H 21 M]: You don't see that here.
#
#
# BUG... someone else kills my old mob:
# "Your enemy, the shepherd had been defeated"
# while I'm healing up and stops the cast thread,
# or I'm in combat and stop fighting.
#  Edit the combat thread stopping logic to compare the kk target to the mob
#  that died.
# PLAN:  (two fixes)
#  1.  keep track of which mob you are kk ing and cc ing and only stop
#      kk and cc if the mob that died was your target. 
#  2.  engage mobs that attack you.  (DONE)
# COMPLETED: I changed the trigger that stops combat and casting to 
# "Your attack overwhelms the ..."
# when a mob is killed so that should solves the above bugs.
#
#  Bug: When dual wielding the same weapon... when it breaks he 
# will try to put it in his off hand every time... i suppose he needs a 
# way to check which one broke!
#  Fix: Could not check which weapon broke.  Just enter both commands
# 'wie' and 'seco' and hope for the best. 

##########################################################################

# TODO LIST (slash WISH LIST):
#
# do math on tick/vig amounts to determine when to stop vigging
# catch "Please wait x more seconds" on quit attempt
# haste thread (hc and sh), search thread (searchc and ssearch)
# - Rewrite KillThread and CastThread to use the MudReader 
#   instead of the other way around.
# haste, steel bottles, silver chalices.
# restoratives
# ### Someone just flashed,
# Someone just wandered to the out.  (hidden mobs)
# The 2nd actress blocks your exit.  (bug: attacks the 1st actress)
# remove unneccessary __init__s
#
# TODO... implement "wie2" ie. "wie2 spe 4" to wield and second spears.
# TODO... "You feel slower" mid combat causes bot to miss a swing (registers too late)
# TODO... try using 'in' operator instead of list searches.
# TODO... fix rest algorithm not to time out
# TODO... mages cast faster (change timers)
# TODO... a "set chase" functionality which will automatically chase
#       mobs that run or chase command
# TODO... a "keep item" list, sell all, drop all.
# TODO combat with circle
# TODO implement MAXHP, MAXMP,
# TODO reverse engineering ticker timings from Piety and maintain current health
# TODO haste timers and thread.
# TODO remove prints from selling algorithm, handle multiple grey cloaks
# (add numbers and sell in decreasing order, and not sell 'empty strings if
# could not fit)
# TODO do not crash on empty inventory at tip
# TODO check mob level before engaging... not need mana for low level mobs etc.
#  (smarter decide_whether_to_engage, maybe no MONSTER_KILL_LIST, but
#   better lists to determine difficulty and better intelligence as to whether
#   to engage mobs from each list level based on mana/health)
# TODO when bot starts reinitialize things like MOBS_ATTACKING
# TODO Make aura checking a little better
# TODO when healing, instead of draining mana pool on vig, 
#   find a way to only vig until health and mana are the same number 
#   of ticks from max.
# TODO fix parse_inventory_list!!!
# TODO higher level chars should not wait for a tick if it won't get the entire 
#  tick.
# TODO: MOBS_ATTACKING only gets depopulated when the bot is killing mobs.
# If a human player kills mobs then MOBS_ATTACKING fills up, and when bot 
# is started it finds a way to empty the list but not a good way.
# TODO: a Cooldowns data object.
# TODO: Figure out why the info command output isn't always complete...
# the table pruned by the game doesn't get all the way through.
# TODO: make a Monster object.  Reason: right now the bot decides what 
#  what monsters to fight by altering his path (not going to kobold cave.)
#  He should really decide at combat time as well (decide whether to fight 
#  mob should include an aura check).  This is best done with Monster objects.
#  Maybe there's a clever way to do their check for equality so that the string 
#  comparisons can be done in the same way (like if (Monster x == 'acolyte')).  
# TODO: fix bug:
#  Items picked up on the way to the tip after going to the shop may have 
#  value would be dropped at the tip.
#  Fix: will have to keep track of the state of going to the tip and not 
#  drop items that were dropped on the way.  
#  More comprehensive: A database of items to drop and sell would 
#  deprecate the above fix.
# TODO: use items.  Keep like 3 each of steel and chalice and like 8 
# restoratives but otherwise use them up.
#
##########################################################################

# IDEAS for how to improve code:

# idea for a function:
#  MUD_output_check(regex_true, regex_false="regex that won't match", timeout=0.8)
#    checks the MUD_buffer for the regexes
#    returns a match object if regex_true is matched
#    returns null (false) if the regex_false occurs (only purpose is to reduce the amount of time)
#    returns null (false) if the given timeout expires.

# Idea: an "Inventory" object so bot can say "Inventory.getInventoryList()" 
#  - right now the bot types 'i' and calls MudReaderHandler.wait_for_inventory_match()
#  which is what Inventory.getInventoryList() would do.  

# Idea for a driving refactoring pattern: 
# The pattern would be to 
# decouple the bot AI from the commands, and eventually the bot AI would never need 
# to know any commands.  Again: strive to stop bot AI from issuing commands by 
# creating objects.

# I skimmed the python style guide. 
# At the time of writing my style preferences are:
# - CamelCase for class names
# - camelCase starting with small letter for class instances
#     (I intend to get rid of all of this _inst for instances...
# - functions/variables with words separated with underscores
# - function names will likely be verbs and variables nouns.
# The whole program doesn't follow this (yet)
#



##########################################################################

# STRING NOTEPAD for things we might want to match to later
# 
# crits
# You knock the wind out of the x!!
# Your attack knocks the x off balance!!
# The x is caught off guard by your attack!
# Your wind magic buffets the x.
#
# looks
# (S)?[Hh]e could kill you with a needle.   +4
# (S)?[Hh]e should be really hard to kill.  +3
# (S)?[Hh]e should be tough to kill.        +2
# (S)?[Hh]e is a little better than you.    +1
# (S)?[Hh]e is a perfect match for you!     0
# (S)?[Hh]e is not quite as good as you.    -1
# (S)?[Hh]e shouldn't be too tough to kill. -2
# (S)?[Hh]e should be easy to kill.         -3
# You could kill him/her with a needle.     -4

# The goodness here sickens and repels you!
# You currently have no carried inventory.


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
from CrawlThread import CrawlThread
from CommandHandler import CommandHandler
from MudReaderHandler import MudReaderHandler
from MudReaderThread import MudReaderThread
from MudListenerThread import MudListenerThread
from MyBuffer import MyBuffer
from Inventory import *
from BotReactions import *
import Database

character = None
commandHandler = None
mudReaderThread = None
mudReaderHandler = None
inventory = None

def main():
    global tn
    global character
    global commandHandler
    global mudReaderThread
    global mudReaderHandler
    global inventory

    ### DEPENDENCY INJECTION ###

    tn = connect_to_MUD()  # Sets up telnet object
    
    ConsoleHandler = newConsoleHandler() 
    character = Character()
    # Buffer used by MudListener and MudReader
    # MudListener writes to it and MudReader reads from it
    MUDBuffer = MyBuffer()
    mudListenerThread = MudListenerThread(tn, MUDBuffer)
    mudListenerThread.start()
    mudReaderThread = MudReaderThread(MUDBuffer, character, ConsoleHandler)
    mudReaderThread.start()
    mudReaderHandler = MudReaderHandler(mudReaderThread, character)
    commandHandler = CommandHandler(character, mudReaderHandler, tn)
    inventory = Inventory(mudReaderHandler, commandHandler, character)

    # Now that the MUD thread is going I can trust it to issue the 
    # username/password prompts
    issue_name_and_password(tn)

    global bot_thread_inst
    bot_thread_inst = None
    global crawl_thread_inst
    crawl_thread_inst = None

    # Whenever a weapon breaks, the program will automatically try to wield 
    # a new one:
    set_up_auto_wield(character, mudReaderHandler, commandHandler) 
        
    # Main thread will go to having raw_input open all the time.
    watch_user_input(mudReaderHandler, character)   
        # The MUD_read thread quits if it hits
        # and EOF.  watch_user_input watches for
        # that and quits too.

    # Clean exit:  watch_user_input sees the "quit" and sends it, then we
    # get here.  mudReaderThread will quit at the EOF, where we join up.
    
    manageMudReader(mudReaderThread, tn)
    


def manageMudReader(mudReaderThread, tn):
    while (mudReaderThread.is_alive()): 
            mudReaderThread.join(3)  # Wait 3 sec for the other thread to quit.
            if (mudReaderThread.is_alive()):
                mudReaderThread.stop()  # Last resort.

    #Okay, clean exit!
    tn.close();
    #That's all, folks!

    print ("It should be safe to ctrl + c now")
    time.sleep(10) #ctrl+c during this sleep seems to work for now

def connect_to_MUD():
    # This function connects to the MUD, returning the telnet object.
    
    HOST = "mud.landsofstone.org"
    PORT = 4801
    tn = telnetlib.Telnet(HOST,PORT)  #No need to call open (http://www.python.org/doc/2.5.2/lib/module-telnetlib.html)

    return tn

def issue_name_and_password(tn):
    
    if(len(sys.argv) >= 3):
        # Use command line arguments for user name and pass
        send_to_telnet(tn, sys.argv[1])
        send_to_telnet(tn, sys.argv[2])
    else:
        # With the MUD thread going already, there is no need to prompt here.
        send_to_telnet(tn, input())
        #tn.write(raw_input() + '\r')    # send user name
        password = getpass.getpass("")  # getpass arg is a prompt string;
                                    # empty string means don't prompt
        #tn.write(password + '\r')       # send password
        send_to_telnet(tn, password)

    return
    
def set_up_auto_wield(character, mudReaderHandler, commandHandler):
    wield1 = WieldReaction("Your (.*?) breaks and you have to remove it\.", character, commandHandler)
    wield2 = WieldReaction("Your (.*?) shatters\.", character, commandHandler)
    mudReaderHandler.register_reaction(wield1)
    mudReaderHandler.register_reaction(wield2)
    return
    
    
def watch_user_input(mudReaderHandler, character):
    
    # This thread watches user input.  For now it will shovel everything
    # to the MUD
#    global PREV_USER_COMMAND  # Last command that was typed in.
#    global PREV_COMMAND # Last command that was sent to telnet.
    global bot_thread_inst
    global crawl_thread_inst
    
    stopping = False;
    while not stopping:
        try:
            user_input = input(); 
        except (EOFError, KeyboardInterrupt) as e:
            magentaprint("Don't try to crash me!  Use 'quit'.")
            user_input = ""

        # Mass switch on user input to get functionality
        user_input = user_input.lstrip() #Optional
        #PREV_USER_COMMAND = user_input
        if(not mudReaderThread.is_alive()):
            magentaprint("\nWhat happened to read thread?  Time to turf.\n")
            #tn.write(user_input + "\n")
            send_to_telnet(tn, user_input)
            stopping = True
            if(is_bot_running()):
                bot_thread_inst.stop()                
            elif(is_crawl_running()):
                crawl_thread_inst.stop()
        elif(user_input == "quit"):
            # TODO:  correct if MUD prints "Please wait x more seconds"
            # after quit was sent.
            #PREV_COMMAND=user_input
            #tn.write(user_input + "\n")
            send_to_telnet(tn, user_input)
            stopping = True
            if(is_bot_running()):
                bot_thread_inst.stop()
            elif(is_crawl_running()):
                crawl_thread_inst.stop()
        elif(re.match("bot ?$|bot [0-9]+$", user_input)):
            #PREV_COMMAND = user_input
            start_bot(user_input, character, commandHandler) # Code for this at the bottom
        elif(re.match("crawl", user_input)):
            start_crawl(character, commandHandler)
        elif(re.match("stop$", user_input)):
            #PREV_COMMAND = user_input
            stop_bot()
        elif(re.match("fle?$|flee$", user_input)):
            stop_bot()
            commandHandler.process(user_input)  
        else:
            commandHandler.process(user_input)
        



############################## THE ROBOT ####################################

def start_bot(user_input, character, commandHandler):
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
    global crawl_thread_inst
    global mudReaderHandler
    global inventory

    # Check for an argument
    M_obj = re.search("[0-9]+", user_input)
    if (M_obj):
        starting_path = int(M_obj.group(0))
    else:
        starting_path = 0
    
    if (is_script_running()):
        magentaprint("A script is already running, you'll have to stop it.  Use \"stop\".")
    else:
        bot_thread_inst = BotThread(starting_path, character, 
                                        commandHandler, mudReaderHandler,
                                        inventory)
            # Constructor arg is which path to start on.
        bot_thread_inst.start()

    return

def stop_bot():
    global bot_thread_inst
    global crawl_thread_inst
    global mudReaderHandler
    if (is_bot_running()):
        bot_thread_inst.stop()
        mudReaderHandler.unregister_reactions()
    if (is_crawl_running()):
        crawl_thread_inst.stop()
        mudReaderHandler.unregister_reactions()

    return
    

def start_crawl(character, commandHandler):
    global bot_thread_inst
    global crawl_thread_inst
    global mudReaderHandler

    if (is_script_running()):
        magentaprint("A script is already running, you'll have to stop it.  Use \"stop\".")
    else:
        crawl_thread_inst = CrawlThread(character, commandHandler, mudReaderHandler)
        crawl_thread_inst.start()

    return

def is_script_running():
    return is_crawl_running() or is_bot_running()

def is_crawl_running():
    global crawl_thread_inst
    return((crawl_thread_inst != None) and crawl_thread_inst.is_alive())

def is_bot_running():
    global bot_thread_inst
    return (((bot_thread_inst != None) and bot_thread_inst.is_alive()))
    

# All definitions are made, ready to go: call main!!!
# (Maybe rethink program structure later)

#if __name__ == '__main__':
main()