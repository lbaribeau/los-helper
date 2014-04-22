
import threading
from threading import Thread
import atexit 
import time
import re

import misc_functions
from KillThread import *
from CastThread import *
# from CoolAbility import *
# from CoolAbilityThread import *
from ThreadStopper import *
from Database import *
from MudMap import *

class CommandHandler(object):

    def __init__(self, character, mudReaderHandler, telnetHandler, database_file, mud_map):
        self.telnetHandler = telnetHandler
        self.character = character
        self.mudReaderHandler = mudReaderHandler
        self.KillThread = None
        self.CastThread = None
        self.CoolAbilityThread1 = None
        self.CoolAbilityThread2 = None

        database = SqliteDatabase(database_file, threadlocals=True, check_same_thread=False)
        db.initialize(database)
        db.connect()
        self.mud_map = mud_map
        create_tables()
        db.close()

    def stop_KillThread(self, debug_on=False):
        if(self.KillThread != None and self.KillThread.is_alive()):
            self.KillThread.stop()
        elif(debug_on):
            magentaprint("No kk thread to stop.")

    def stop_CastThread(self, debug_on=False):
        if(self.CastThread != None and self.CastThread.is_alive()):
            self.CastThread.stop()
        elif(debug_on):
            magentaprint("No cc thread to stop.")
            
    #TODO: def stop_CoolAbilityThread1(self):
        
    #TODO: def stop_CoolAbilityThread2(self):


    def process(self, user_input):
        """ This CommandHandler function is the filter for user input that
        does some matching and calls functions based on that input.  The only
        commands that don't make it this far are 'quit', 'bot' and 'stop'.
        The reason for that is I didn't want CommandHandler to have to know
        at all about the bot, so the upper layer intercepts the relevant
        commands.  Also, when the bot is stopped on a flee, the calling layer
        handles stopping the bot."""

        if re.match("ga$", user_input):
            self.telnetHandler.write("get all")
        elif re.match("ki? [a-zA-Z]|kill? [a-zA-Z]", user_input):
            self.user_ki(user_input)
        elif re.match("kk ", user_input):
            self.user_kk(user_input[3:].lstrip())
        elif re.match("sk$", user_input):
            self.user_sk()
        elif re.match("cc ", user_input):
            self.user_cc(user_input[3:].lstrip())
        elif re.match("sc$", user_input):
            self.user_sc()
        elif re.match("dro? ", user_input):
            self.user_dr(user_input)
        elif re.match("ca? [a-zA-Z]|cast? [a-zA-Z]", user_input):
            self.user_ca(user_input)
        elif re.match("n$", user_input) or re.match("s$", user_input) or \
             re.match("e$", user_input) or re.match("w$", user_input) or \
             re.match("nw$", user_input) or re.match("ne$", user_input) or \
             re.match("se$", user_input) or re.match("sw$", user_input) or \
             re.match("u$", user_input) or re.match("d$", user_input) or \
             re.match("ou[t]?$", user_input) or re.match("go ",user_input):
            self.character.TRYING_TO_MOVE = True
            self.character.LAST_DIRECTION = user_input.replace("go ", "")
            self.user_move(user_input)
            # routine which does appropriate waiting,
            # printing, and finally sending command.
        elif(re.match("find (.+)", user_input)):
            M_obj = re.search("find (.+)", user_input)
            magentaprint("Finding: " + str(M_obj.group(1)))
            MudMap.find(str(M_obj.group(1)))

        elif re.match("wie?2 +[a-zA-Z]+( +\d+)?", user_input):
            user_input = "wield " + user_input[3:] 
            self.telnetHandler.write(user_input)
            #self.user_wie2(user_input[4:].lstrip())
        elif re.match("fle?$|flee$", user_input):
            self.user_flee()
        elif re.match("HASTING", user_input):  # Debug
            magentaprint(str(self.character.HASTING))
        elif re.match("WEAPON1", user_input):
            magentaprint(self.character.WEAPON1)
        elif re.match("WEAPON2", user_input):
            magentaprint(self.character.WEAPON2)
        elif re.match("MONSTER_CHECK_FLAG", user_input):
            magentaprint(str(self.character.MONSTER_CHECK_FLAG))
        elif re.match("MONSTER_LIST", user_input):
            magentaprint(str(self.character.MONSTER_LIST), False)
        elif re.match("AREA_ID", user_input):
            magentaprint("<" + str(self.character.AREA_ID) + ">", False)
        elif re.match("LAST_DIR", user_input):
            magentaprint("<" + str(self.character.LAST_DIRECTION) + ">", False)
        elif re.match("AREA_TITLE", user_input):
            magentaprint("<" + str(self.character.AREA_TITLE) + ">", False)
        elif re.match("EXIT_LIST", user_input):
            magentaprint(str(self.character.EXIT_LIST), False)
        elif re.match("HEALTH", user_input):
            magentaprint(str(self.character.HEALTH), False)
        elif re.match("EXPERIENCE", user_input):
            exp = self.character.EXPERIENCE
            expm = str(calculate_vpm(exp))
            magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, False)
            #magentaprint(str(exp), False)
        elif re.match("GOLD", user_input):
            #gold = self.character.GOLD  #Calculating GMP would require us to store gold differently
            #gpm = str(calculate_vpm(gold))
            #magentaprint("Gold this Session: " + str(gold) + " | Gold / MIN: " + gpm, False)
            magentaprint(str(self.character.GOLD), False)
        elif re.match("KILLS", user_input):
            kills = self.character.MOBS_KILLED
            kpm = str(calculate_vpm(kills))
            magentaprint("Kills this Session: " + str(kills) + " | Kills / MIN: " + kpm, False)
        elif re.match("DUMP", user_input):
            magentaprint(self.character.__dict__, False)
        elif re.match("VERSION", user_input):
            magentaprint("Version: " + str(misc_functions.VERSION), False)
            magentaprint(self.character.__dict__, False)
        elif re.match("REPORT", user_input):
            self.process("info")
            time.sleep(1)
            exp = self.character.TOTAL_EXPERIENCE
            gold = self.character.TOTAL_GOLD
            magentaprint("Total EXP: " + str(exp) + " | Total Gold: " + str(gold), False)
            exp = self.character.EXPERIENCE
            expm = str(calculate_vpm(exp))
            magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, False)
            kills = self.character.MOBS_KILLED
            kpm = str(calculate_vpm(kills))
            magentaprint("Kills this Session: " + str(kills) + " | Kills / MIN: " + kpm, False)
            runtime = get_runtime_in_minutes()
            magentaprint("Minutes Run: " + str(runtime), False)
        elif re.match("MUD_RETURN_ITEM_SOLD", user_input):
            magentaprint(self.character.MUD_RETURN_ITEM_SOLD)
        elif re.match("MOBS_JOINED_IN", user_input):
            magentaprint(self.character.MOBS_JOINED_IN)
        elif re.match("AURA", user_input):
            magentaprint(str(self.character.AURA), False)        
        elif re.match("MOBS_ATTACKING", user_input):
            magentaprint(self.character.MOBS_ATTACKING)
        elif re.match("MONSTER_KILL_LIST", user_input):
            magentaprint(str(self.character.MONSTER_KILL_LIST))
        elif re.match("reactionlist", user_input):
            for r in self.mudReaderHandler.MudReaderThread.BotReactionList:
                magentaprint('    ' + str(r))
        elif re.match("cackle", user_input):
            misc_functions.verboseMode = not misc_functions.verboseMode
            magentaprint("Verbose mode changed", False)
        elif re.match("defecate", user_input):
            misc_functions.debugMode = not misc_functions.debugMode
            magentaprint("Debug Mode changed", False)
        elif re.match(str(self.character.EXIT_REGEX), user_input):
            self.character.LAST_DIRECTION = user_input.replace("go ", "")
            self.character.TRYING_TO_MOVE = True
            self.user_move("go " + self.character.LAST_DIRECTION)
            magentaprint("Running go on EXIT_REGEX: " + str(self.character.EXIT_REGEX), False)
        else: # Doesn't match any command we are looking for
            self.telnetHandler.write(user_input) # Just shovel to telnet.


    def user_ki(self, user_input):
        now = time.time()
        time_remaining = self.character.ATTACK_WAIT - (now - self.character.ATTACK_CLK)
        if time_remaining < 0:
            self.character.ATTACK_CLK = now
            self.telnetHandler.write(user_input)
        elif time_remaining < 1.0:
            magentaprint("Delaying by %.1f sec ..." % time_remaining, False)
            time.sleep(time_remaining)
            magentaprint("Sent.", False)
            self.character.ATTACK_CLK = now
            self.telnetHandler.write(user_input)
        else:
            magentaprint("(Python) Wait %.1f more seconds" % time_remaining, False)

            
    def user_ca(self, user_input):
        # TODO: Match this to a spell list so I can actually tell if they
        # issued a valid command.  Then maybe issue quicker feedback
        # than the MUD can!.
        # Casting something... do anything here?  Just set clock.
        # Check if you can cast.

        now = time.time()
        time_remaining = self.character.CAST_WAIT - (now - self.character.CAST_CLK) # cast time only depends
                                                    # on last cast (even if it failed!)
        if time_remaining < 0:
            self.character.CAST_CLK = now
            self.telnetHandler.write(user_input)
        elif time_remaining < 1.0:
            magentaprint("(Python) Delaying by %.1f sec ... " % time_remaining, False)
            time.sleep(time_remaining)
            magentaprint("Sent.", False)
            self.character.CAST_CLK = now
            self.telnetHandler.write(user_input)
        else:
            magentaprint("(Python) Wait %.1f more seconds" % time_remaining, False)


    def user_move(self, user_input):
        self.stop_KillThread()
        self.stop_CastThread()

        now = time.time()
        
        wait_from_move = self.character.MOVE_WAIT - (now - self.character.MOVE_CLK)
        wait_from_ATTACK = self.character.ATTACK_WAIT - (now - self.character.ATTACK_CLK)
        wait_from_CAST = self.character.CAST_WAIT - (now - self.character.CAST_CLK)
        
        time_remaining = max(wait_from_move, wait_from_ATTACK, wait_from_CAST);
        
        #magentaprint("MOVE wait time: %f" % wait_from_move)
        #magentaprint("ATTACK wait time: %f" % wait_from_ATTACK)
        #magentaprint("CAST wait time: %f" % wait_from_CAST)
          
        if time_remaining < 0:
            self.character.MOVE_CLK = now
            self.telnetHandler.write(user_input)
        elif time_remaining < 1.0:
            magentaprint("(Python) Delaying by %.1f sec ..." % time_remaining, False)
            time.sleep(time_remaining)
            magentaprint("Sent.", False)
            self.character.MOVE_CLK = now
            self.telnetHandler.write(user_input)
        else:
            magentaprint("Wait %.1f more seconds" % time_remaining, False)
        
    def stop_KillThread(self):
        if self.KillThread != None and self.KillThread.is_alive():
            self.KillThread.stop()

    def stop_CastThread(self):
        if self.CastThread != None and self.CastThread.is_alive():
            self.CastThread.stop()

    def user_dr(self, user_input):
        [command, item] = user_input.split(" ", 1)
        user_input = "drop " + item
        self.telnetHandler.write(user_input)
    
    def user_kk(self, argv):
        if self.KillThread != None and self.KillThread.is_alive():
            # Commenting... tried doing registering reactions here but maybe 
            # it's better for KillThread to do it.
            #if(self.KillThread.get_stopping() == True):
            #    self.KillThread.keep_going()
            #    self.KillThread.set_target(argv)
            #    self._do_kill_reactions() 
            #      # Assumes that when stop is called the kill reactions were unregistered,
            #      # so we have to redo the kill reactions.  They would have been undone
            #      # Or, maybe I could make 'stop' work immediately.  Nah, try having 
            #      # KillThread do the registering.
            #else:
            #    self.KillThread.set_target(argv)                
            self.KillThread.set_target(argv)
            self.KillThread.keep_going()
        else:
            self.KillThread = KillThread(self.character, self.mudReaderHandler, self.telnetHandler, argv)
            self.KillThread.start()
            #self._do_kill_reactions()

    
    def user_sk(self):
        self.stop_KillThread()
        self.telnetHandler.write("")
    

    def user_cc(self, argv):
        # TODO: Bug for user input "cc "
        if argv == "":
            magentaprint("Usage:  cc <spell> [<target> [<number>]]", False)
            self.telnetHandler.write("") # TODO: Keep a prompt up to date so we can print
                                    # immediately instead of sending to mud.
            return        
        elif re.search(argv, " "):
            [spell, target] = argv.split(" ",1)
        else:
            spell = argv
            target = ""
        
        if self.CastThread != None and self.CastThread.is_alive():
            magentaprint("Updating existing cast thread.")
            self.CastThread.set_spell(spell)
            self.CastThread.set_target(target)
            self.CastThread.keep_going()
        else:
            magentaprint("New instance of cc thread")
            self.CastThread = CastThread(self.character, 
                                         self.mudReaderHandler, 
                                         self.telnetHandler, 
                                         spell, 
                                         target)
            self.CastThread.start()      


    def user_sc(self):
        self.stop_CastThread()
        self.telnetHandler.write("")

    
    def user_wie2(self, argv):
        self.telnetHandler.write("wield %s\n" % (argv))
        self.telnetHandler.write("second %s\n" % (argv))

    
    # COOL ABILITIES
    def user_hastec(self):        
        if((self.CoolAbilityThread1 != None and 
            self.CoolAbilityThread1.is_alive() and
            self.CoolAbilityThread1.CoolAbility.getCommand().isequal("haste")) 
            or
            (self.CoolAbilityThread2 != None and 
            self.CoolAbilityThread2.is_alive() and
            self.CoolAbilityThread2.CoolAbility.getCommand().isequal("haste"))):
            # Already running a thread
            magentaprint("Haste thread already going.")
        else:
            magentaprint("CommandHandler: new haste thread")
            if self.CoolAbilityThread1 == None or not self.CoolAbilityThread1.is_alive():
                self.CoolAbilityThread1 = CoolAbilityThread(Haste(), self.mudReaderHandler, self.telnetHandler)
                self.CoolAbilityThread1.start()
            elif self.CoolAbilityThread2 == None or not self.CoolAbilityThread2.is_alive():
                self.CoolAbilityThread2 = CoolAbilityThread(Haste(), self.mudReaderHandler, self.telnetHandler)
                self.CoolAbilityThread2.start()
            else: 
                magentaprint("Error! both CoolAbilityThreads are unavailable!")

    
    def user_flee(self):
        self.stop_CastThread()
        now = time.time()
        time_remaining = max(self.character.MOVE_WAIT - (now - self.character.MOVE_CLK),
                             self.character.ATTACK_WAIT - (now - self.character.ATTACK_CLK),
                             self.character.CAST_WAIT - (now - self.character.CAST_CLK))
        magentaprint("Fleeing in %.1f sec ..." % time_remaining, False)
        first_sleep = max(time_remaining - self.character.ATTACK_WAIT - 0.2, 0)
        second_sleep = time_remaining - first_sleep 
        time.sleep(first_sleep)

        # This sleep will allow KillThread to get one more swing in if there is time for it.
        # So we wait until time_remaining is 3 before stopping KillThread
        self.stop_KillThread()
        magentaprint("KillThread is stopped, %.1f until escape." % time_remaining, False)

        if self.character.WEAPON1 != "":
            self.telnetHandler.write("rm " + self.character.WEAPON1)
        if self.character.WEAPON2 != "":
            self.telnetHandler.write("rm " + self.character.WEAPON2)

        if second_sleep < 0.1:
            second_sleep = 0.1

        time.sleep(second_sleep)
        
        now = time.time()
        time_remaining = max(self.character.MOVE_WAIT - (now - self.character.MOVE_CLK),
                             self.character.ATTACK_WAIT - (now - self.character.ATTACK_CLK),
                             self.character.CAST_WAIT - (now - self.character.CAST_CLK))

        self.character.MOVE_CLK = now
            
        # Note: in very few rare cases it may be better to flee once.  
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")
        magentaprint("Sent.", False)

        manage_telnet_output("I had to run - sorry....", False)  
           # TODO: This should not print when human user runs
           # And perhaps "manage_telnet_output" does not describe well what is happening here...
           # Also, it should be magenta.

        time.sleep(0.1)  

        if self.character.WEAPON1 != "":
            self.telnetHandler.write("wie " + self.character.WEAPON1)
        if self.character.WEAPON2 != "":
            self.telnetHandler.write("wie " + self.character.WEAPON2)

    def get_directions_from_where_we_are_to_area_id(self, to_area_id):
        directions = []
        try:
            if self.character.AREA_ID is not None:
                directions = self.mud_map.get_path(int(self.character.AREA_ID), int(to_area_id))
            else:
                magentaprint("I'm not sure where I am (CurAreaID: " + str(self.character.AREA_ID) + ")", False)
        except Exception:
            magentaprint("I couldn't find a way there (" + str(self.character.AREA_ID) + ") to (" + str(to_area_id) + ")",False)
        return directions
