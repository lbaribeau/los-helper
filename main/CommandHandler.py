
import threading
from threading import Thread
import atexit 
import time
import re

from misc_functions import *
from KillThread import *
from CastThread import *

class CommandHandler:

    def __init__(self, Character_inst_in, tn_in):
        self.tn = tn_in
        self.Character_inst = Character_inst_in
        self.KillThread_inst = None
        self.CastThread_inst = None
        pass

    def stop_KillThread(self, debug_on=False):
        if(self.KillThread_inst != None and self.KillThread_inst.is_alive()):
            self.KillThread_inst.stop()
        elif(debug_on):
            magentaprint("No kk thread to stop.")

    def stop_CastThread(self, debug_on=False):
        if(self.CastThread_inst != None and self.CastThread_inst.is_alive()):
            self.CastThread_inst.stop()
        elif(debug_on):
            magentaprint("No cc thread to stop.")


    def process(self, user_input):
        """ This CommandHandler function is the filter for user input that
        does some matching and calls functions based on that input.  The only
        commands that don't make it this far are 'quit', 'bot' and 'stop'.
        The reason for that is I didn't want CommandHandler to have to know
        at all about the bot, so the upper layer intercepts the relevant
        commands.  Also, when the bot is stopped on a flee, the calling layer
        handles stopping the bot."""
        if(re.match("ga$", user_input)):
            #PREV_COMMAND = user_input
            self.tn.write("get all\n")
        elif(re.match("ki? [a-zA-Z]|kill? [a-zA-Z]", user_input)):
            #PREV_COMMAND = user_input
            self.user_ki(user_input) # routine which does appropriate waiting,
                                # printing, and finally sending command.
        elif(re.match("kk ", user_input)):
            self.user_kk(user_input[3:].lstrip())
        elif(re.match("sk$", user_input)):
            #PREV_COMMAND = user_input
            self.user_sk()
        elif(re.match("cc ", user_input)):
            self.user_cc(user_input[3:].lstrip())
        elif(re.match("sc$", user_input)):
            self.user_sc()
        elif(re.match("dro? ", user_input)):
            #PREV_COMMAND = user_input
            self.user_dr(user_input)
        elif(re.match("ca? [a-zA-Z]|cast? [a-zA-Z]", user_input)):
            #PREV_COMMAND=user_input
            self.user_ca(user_input) # routine which does appropriate waiting,
                                # printing, and finally sending command.              
        elif(   re.match("n$",user_input) or re.match("s$",user_input) or
                re.match("e$",user_input) or re.match("w$",user_input) or
                re.match("nw$",user_input) or re.match("ne$",user_input) or
                re.match("se$",user_input) or re.match("sw$",user_input) or
                re.match("u$",user_input) or re.match("d$", user_input) or 
                re.match("ou[t]?$", user_input) or re.match("go ",user_input) ):
            #PREV_COMMAND=user_input
            self.user_move(user_input) 
            # routine which does appropriate waiting,
            # printing, and finally sending command.
        
        # Wielding?  Just do an alias here and do the current weapon maintenance
        # upon reading the MUD.  Reason: I don't know here whether he is
        # wielding a valid weapon and that way I don't have to recover in case
        # he can't wield it.
        elif(re.match("wie? [a-zA-Z]|wield? [a-zA-Z]", user_input)):
            #Alias
            if(re.match("wi [a-zA-Z]", user_input)):
                user_input = "wield " + user_input[3:]
            #PREV_COMMAND = user_input
            self.tn.write(user_input + "\n")
        elif(re.match("fle?$|flee$", user_input)):
            # Fleeing.  Call routine to stop all combat threads, remove weapons,
            # and flee ASAP
            #PREV_COMMAND = user_input
            self.user_flee()
        elif(re.match("HASTING", user_input)):  # Debug
            #user_hk(user_input[3:].lstrip()) Deprecated!
            magentaprint(str(self.Character_inst.HASTING))
        elif(re.match("WEAPON1", user_input)):
            magentaprint(self.Character_inst.WEAPON1)
        elif(re.match("WEAPON2", user_input)):
            magentaprint(self.Character_inst.WEAPON2)
        elif(re.match("MONSTER_CHECK_FLAG", user_input)):
            magentaprint(str(self.Character_inst.MONSTER_CHECK_FLAG))
        elif(re.match("MONSTER_LIST", user_input)):
            magentaprint(str(self.Character_inst.MONSTER_LIST))
        elif(re.match("HEALTH", user_input)):
            magentaprint(str(self.Character_inst.HEALTH))
        elif(re.match("INVENTORY_LIST", user_input)):
            magentaprint(str(self.Character_inst.INVENTORY_LIST))
        elif(re.match("EXPERIENCE", user_input)):
            magentaprint(self.Character_inst.EXPERIENCE)
        elif(re.match("GOLD", user_input)):
            magentaprint(self.Character_inst.GOLD)
        elif(re.match("MUD_RETURN_ITEM_SOLD", user_input)):
            magentaprint(self.Character_inst.MUD_RETURN_ITEM_SOLD)
        elif(re.match("MOBS_JOINED_IN", user_input)):
            magentaprint(self.Character_inst.MOBS_JOINED_IN)
        elif(re.match("AURA", user_input)):
            magentaprint(self.Character_inst.AURA)        
        elif(re.match("MOBS_ATTACKING", user_input)):
            magentaprint(self.Character_inst.MOBS_ATTACKING)
        elif(re.match("MONSTER_KILL_LIST", user_input)):
            magentaprint(str(self.Character_inst.MONSTER_KILL_LIST))            
        else: # Doesn't match any command we are looking for
            self.tn.write(user_input + "\n") # Just shovel to telnet.

    def user_ki(self, user_input):
        #global ATTACK_CLK, ATTACK_WAIT
        now = time.time()
        time_remaining = self.Character_inst.ATTACK_WAIT - (now -self.Character_inst.ATTACK_CLK)
        if (time_remaining < 0):
            self.Character_inst.ATTACK_CLK = now
            self.tn.write(user_input + "\n")
        elif(time_remaining < 1.0):
            magentaprint("Delaying by %.1f sec ..." % time_remaining)
            time.sleep(time_remaining)
            magentaprint("Sent.")
            self.Character_inst.ATTACK_CLK = now
            self.tn.write(user_input + "\n")
        else:
            magentaprint("(Python) Wait %.1f more seconds" % time_remaining)
            
    def user_ca(self, user_input):
        # TBD: Match this to a spell list so I can actually tell if they
        # issued a valid command.  Then maybe issue quicker feedback
        # than the MUD can!.
        # Casting something... do anything here?  Just set clock.
        # Check if you can cast.
        #print "Starting cast clock"
        #global CAST_CLK, CAST_WAIT
        #global character_inst
        now = time.time()
        time_remaining = self.Character_inst.CAST_WAIT - (now - self.Character_inst.CAST_CLK) # cast time only depends
                                                    # on last cast (even if it
                                                    # failed!
        if (time_remaining < 0):
            self.Character_inst.CAST_CLK = now
            self.tn.write(user_input + "\n")
        elif (time_remaining < 1.0):
            magentaprint("(Python) Delaying by %.1f sec ... " % time_remaining)
            time.sleep(time_remaining)
            magentaprint("Sent.")
            self.Character_inst.CAST_CLK = now
            self.tn.write(user_input + "\n")
        else:
            magentaprint("(Python) Wait %.1f more seconds" % time_remaining)


    def user_move(self, user_input):
        #global character_inst
        #global MOVE_WAIT, MOVE_CLK, ATTACK_WAIT, ATTACK_CLK, CAST_WAIT, CAST_CLK
        
        # They're trying to leave... stop kk and cc
        self.stop_KillThread()
        self.stop_CastThread()

        # Wait appropriate amount if necessary.            
        now = time.time()
        
        wait_from_move = self.Character_inst.MOVE_WAIT - (now - self.Character_inst.MOVE_CLK)
        wait_from_ATTACK = self.Character_inst.ATTACK_WAIT - (now - self.Character_inst.ATTACK_CLK)
        wait_from_CAST = self.Character_inst.CAST_WAIT - (now - self.Character_inst.CAST_CLK)
        
        time_remaining = max(wait_from_move, wait_from_ATTACK, wait_from_CAST);
        
        #magentaprint("MOVE wait time: %f" % wait_from_move)
        #magentaprint("ATTACK wait time: %f" % wait_from_ATTACK)
        #magentaprint("CAST wait time: %f" % wait_from_CAST)
          
        if (time_remaining < 0):
            self.Character_inst.MOVE_CLK = now
            self.tn.write(user_input + "\n")
        elif(time_remaining < 1.0):
            # Less than a second, just do the delay for them.
            magentaprint("(Python) Delaying by %.1f sec ..." % time_remaining)
            time.sleep(time_remaining)
            magentaprint("Sent.")
            self.Character_inst.MOVE_CLK = now
            self.tn.write(user_input + "\n")
        else:
            magentaprint("(Python) Wait %.1f more seconds" % time_remaining)


    def user_dr(self, user_input):
        #M_obj = re.match("dro?", user_input)
        #if(M_obj != None):
        [command, item] = user_input.split(" ",1)
        user_input = "drop " + item
        self.tn.write(user_input + "\n")
        return
    
    def user_kk(self, argv):
        # This is what to do if user inputs "kk"
        # We've got the string to work with.
        # This function will send "k " + argv every three seconds.
        # This will get its own thread, user_KillThread, which is started here.

        #global user_KillThread_inst
        
        if (self.KillThread_inst != None and self.KillThread_inst.is_alive()):
            self.KillThread_inst.set_target(argv)
            self.KillThread_inst.keep_going()
        else:
            self.KillThread_inst = KillThread(self.Character_inst, self.tn, argv)
            self.KillThread_inst.start()

    
    def user_sk(self):
        # This function is called when the user typed sk.  That means we want
        # to quit attacking.
#        global KillThread_inst
#        if(self.kk_thread_inst != None and self.kk_thread_inst.is_alive()):
#            self.kk_thread_inst.stop()
#        else:
#            magentaprint("Nothing to stop.")
#        tn.write("\n")  # brings prompt back as if this command were a normal one
#        return
        self.stop_KillThread(True)
        self.tn.write("\n")  # brings prompt back as if this command were a normal one
        return
    

    def user_cc(self, argv):
        # This is what to do if user inputs "cc"
        # We've got the string to work with.
        # This function will send "c " + argv every three seconds.
        # This will get its own thread, KillThread, which is started here.

        #global CastThread_inst

        # Get strings spell and target
        # BUG!! user input "cc "
        if(argv == ""):
            # Do nothing.
            magentaprint("Usage:  cc <spell> [<target> [<number>]]")
            tn.write("\n")  # TBD: Keep a prompt up to date so we can print
                            # immediately instead of sending to mud.
            return        
        elif(re.search(argv, " ")): # If it has one or more spaces
            #print("<"+argv+">")
            [spell, target] = argv.split(" ",1)
        else:
            spell = argv
            target = ""
        # spell is either empty or one string,
        # target may be empty, one target, or even have a space
        
        if (self.CastThread_inst != None and self.CastThread_inst.is_alive()):
            # Already casting - just update spell and target.
            magentaprint("Already had an instance... updating it")
            self.CastThread_inst.set_spell(spell)
            self.CastThread_inst.set_target(target)
            self.CastThread_inst.keep_going()
        else:
            # Start new instance
            magentaprint("New instance of cc thread")
            self.CastThread_inst = CastThread(self.Character_inst, self.tn, spell, target)
            self.CastThread_inst.start()      


    def user_sc(self):
        # This function is called when the user typed sk.  That means we want
        # to quit attacking.
#        global CastThread_inst
#        if(CastThread_inst != None and CastThread_inst.is_alive()):
#            CastThread_inst.stop()
#        else:
#            magentaprint("Nothing to stop.")   
#        tn.write("\n")  # brings prompt back as if this command were a normal one
        self.stop_CastThread(True)
        self.tn.write("\n")  # brings prompt back as if this command were a normal one
        return

    
    def user_flee(self):
        
    #    global WEAPON1
    #    global WEAPON2
    #    global MOVE_WAIT, MOVE_CLK, ATTACK_WAIT, ATTACK_CLK, CAST_WAIT, CAST_CLK
        #global character_inst


        # Stop the bot.
        # NOPE: NOW TRUSTING HIGHER LEVEL TO STOP BOT (NOT IN MY SCOPE)
        #if(bot_thread_inst != None and bot_thread_inst.is_alive()):
        #    bot_thread_inst.stop()
        
        # Stop combat threads.
        #if(KillThread_inst != None and KillThread_inst.is_alive()):
        #    KillThread_inst.stop()
        #if(CastThread_inst != None and CastThread_inst.is_alive()):
        #    CastThread_inst.stop()
        self.stop_KillThread()
        self.stop_CastThread()

        # Remove weapons.
        if(self.Character_inst.WEAPON1 != ""):
            self.tn.write("rm " + self.Character_inst.WEAPON1 + "\n")
        #    WEAPON1 = ""
        if(self.Character_inst.WEAPON2 != ""):
            self.tn.write("rm " + self.Character_inst.WEAPON2 + "\n")
        #    WEAPON2 = ""

        # Do the timing dance.
        # Actually, this may as well be a thread because I don't want to block
        # user input.  NO.  No need to time flee attempts.  Same timer as attack.
        # No time constraints on flee attempts.

        # Keep it simple.  Wait till ready then flee several times.  (beats
        # failed to escape)
        # TBD: Print if its more than a second... but I don't think that's
        # necessary
        #wait_for_attack_ready()
        #wait_for_cast_ready()
        
        now = time.time()
        time_remaining = max(self.Character_inst.MOVE_WAIT - (now - self.Character_inst.MOVE_CLK),
                             self.Character_inst.ATTACK_WAIT - (now - self.Character_inst.ATTACK_CLK),
                             self.Character_inst.CAST_WAIT - (now - self.Character_inst.CAST_CLK))
        if (time_remaining < 0):
            self.Character_inst.MOVE_CLK = now
        else:
            magentaprint("(Python) Delaying by %.1f sec ..." % time_remaining)
            time.sleep(time_remaining)
            magentaprint("Sent.")
            self.Character_inst.MOVE_CLK = now
            
        # Alternative is to check on MUD out for flee failures but that's not even
        # necessary!.
        # Note, it might be better in some cases just to flee once.  I think I will
        # implement "fl1" for that case.  (TBD)
        self.tn.write("fl\n")
        self.tn.write("fl\n")
        self.tn.write("fl\n")

        # Put weapons back on.
        time.sleep(0.1)
        if(self.Character_inst.WEAPON1 != ""):
            self.tn.write("wie " + self.Character_inst.WEAPON1 + "\n")
        if(self.Character_inst.WEAPON2 != ""):
            self.tn.write("seco " + self.Character_inst.WEAPON2 + "\n")

        return    
        

