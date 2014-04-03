
import threading
from threading import Thread
import atexit 
import time
import re

from misc_functions import *
from KillThread import *
from CastThread import *
from CoolAbility import *
from CoolAbilityThread import *
from ThreadStopper import *


class CommandHandler:

    def __init__(self, Character, MudReaderHandler, tn_in):
        self.tn = tn_in
        self.Character = Character
        self.MudReaderHandler = MudReaderHandler
        self.KillThread = None
        self.CastThread = None
        self.CoolAbilityThread1 = None
        self.CoolAbilityThread2 = None
        pass

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
        if(re.match("ga$", user_input)):
            #PREV_COMMAND = user_input
            #self.tn.write("get all\n")
            send_to_telnet(self.tn, "get all")
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
            #self.tn.write(user_input + "\n")
            send_to_telnet(self.tn, user_input)
        elif(re.match("wie?2 +[a-zA-Z]+( +\d+)?", user_input)):
            self.user_wie2(user_input[4:].lstrip())
        elif(re.match("fle?$|flee$", user_input)):
            #PREV_COMMAND = user_input
            self.user_flee()
        elif(re.match("HASTING", user_input)):  # Debug
            #user_hk(user_input[3:].lstrip()) Deprecated!
            magentaprint(str(self.Character.HASTING))
        elif(re.match("WEAPON1", user_input)):
            magentaprint(self.Character.WEAPON1)
        elif(re.match("WEAPON2", user_input)):
            magentaprint(self.Character.WEAPON2)
        elif(re.match("MONSTER_CHECK_FLAG", user_input)):
            magentaprint(str(self.Character.MONSTER_CHECK_FLAG))
        elif(re.match("MONSTER_LIST", user_input)):
            magentaprint(str(self.Character.MONSTER_LIST))
        elif(re.match("HEALTH", user_input)):
            magentaprint(str(self.Character.HEALTH))
        elif(re.match("INVENTORY_LIST", user_input)):
            magentaprint(str(self.Character.INVENTORY_LIST))
        elif(re.match("EXPERIENCE", user_input)):
            magentaprint(self.Character.EXPERIENCE)
        elif(re.match("GOLD", user_input)):
            magentaprint(self.Character.GOLD)
        elif(re.match("MUD_RETURN_ITEM_SOLD", user_input)):
            magentaprint(self.Character.MUD_RETURN_ITEM_SOLD)
        elif(re.match("MOBS_JOINED_IN", user_input)):
            magentaprint(self.Character.MOBS_JOINED_IN)
        elif(re.match("AURA", user_input)):
            magentaprint(self.Character.AURA)        
        elif(re.match("MOBS_ATTACKING", user_input)):
            magentaprint(self.Character.MOBS_ATTACKING)
        elif(re.match("MONSTER_KILL_LIST", user_input)):
            magentaprint(str(self.Character.MONSTER_KILL_LIST))
        elif(re.match("reactionlist", user_input)):
            for r in self.MudReaderHandler.MudReaderThread.BotReactionList:
                magentaprint('    ' + str(r))
<<<<<<< HEAD
        else: # Doesn't match any command we are looking for
            #@self.tn.write(user_input + "\n") # Just shovel to telnet.
            send_to_telnet(self.tn, user_input)
=======
        else: 
            self.tn.write(user_input + "\n")
>>>>>>> origin/master

    def user_ki(self, user_input):
        #global ATTACK_CLK, ATTACK_WAIT
        now = time.time()
        time_remaining = self.Character.ATTACK_WAIT - (now - self.Character.ATTACK_CLK)
        if (time_remaining < 0):
            self.Character.ATTACK_CLK = now
            #self.tn.write(user_input + "\n")
            send_to_telnet(self.tn, user_input)
        elif(time_remaining < 1.0):
            magentaprint("Delaying by %.1f sec ..." % time_remaining)
            time.sleep(time_remaining)
            magentaprint("Sent.")
            self.Character.ATTACK_CLK = now
            #self.tn.write(user_input + "\n")
            send_to_telnet(self.tn, user_input)
        else:
            magentaprint("(Python) Wait %.1f more seconds" % time_remaining)
            
    def user_ca(self, user_input):
        # TODO: Match this to a spell list so I can actually tell if they
        # issued a valid command.  Then maybe issue quicker feedback
        # than the MUD can!.
        # Casting something... do anything here?  Just set clock.
        # Check if you can cast.

        now = time.time()
        time_remaining = self.Character.CAST_WAIT - (now - self.Character.CAST_CLK) # cast time only depends
                                                    # on last cast (even if it failed!)
        if (time_remaining < 0):
            self.Character.CAST_CLK = now
            #self.tn.write(user_input + "\n")
            send_to_telnet(self.tn, user_input)
        elif (time_remaining < 1.0):
            magentaprint("(Python) Delaying by %.1f sec ... " % time_remaining)
            time.sleep(time_remaining)
            magentaprint("Sent.")
            self.Character.CAST_CLK = now
            #self.tn.write(user_input + "\n")
            send_to_telnet(self.tn, user_input)
        else:
            magentaprint("(Python) Wait %.1f more seconds" % time_remaining)


    def user_move(self, user_input):
        self.stop_KillThread()
        self.stop_CastThread()

        now = time.time()
        
        wait_from_move = self.Character.MOVE_WAIT - (now - self.Character.MOVE_CLK)
        wait_from_ATTACK = self.Character.ATTACK_WAIT - (now - self.Character.ATTACK_CLK)
        wait_from_CAST = self.Character.CAST_WAIT - (now - self.Character.CAST_CLK)
        
        time_remaining = max(wait_from_move, wait_from_ATTACK, wait_from_CAST);
        
        #magentaprint("MOVE wait time: %f" % wait_from_move)
        #magentaprint("ATTACK wait time: %f" % wait_from_ATTACK)
        #magentaprint("CAST wait time: %f" % wait_from_CAST)
          
        if (time_remaining < 0):
            self.Character.MOVE_CLK = now
            send_to_telnet(self.tn, user_input)
        elif(time_remaining < 1.0):
            magentaprint("(Python) Delaying by %.1f sec ..." % time_remaining)
            time.sleep(time_remaining)
            magentaprint("Sent.")
            self.Character.MOVE_CLK = now
            #self.tn.write(user_input + "\n")
            send_to_telnet(self.tn, user_input)
        else:
            magentaprint("Wait %.1f more seconds" % time_remaining)


    def user_dr(self, user_input):
        [command, item] = user_input.split(" ", 1)
        user_input = "drop " + item
        #self.tn.write(user_input + "\n")
        send_to_telnet(self.tn, user_input)
        return
    
    def user_kk(self, argv):
        if (self.KillThread != None and self.KillThread.is_alive()):
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
            self.KillThread = KillThread(self.Character, self.MudReaderHandler, self.tn, argv)
            self.KillThread.start()
            #self._do_kill_reactions()

    
    def user_sk(self):
        self.stop_KillThread(True)
        #self.tn.write("\n")  # brings prompt back as if this command were a normal one
        send_to_telnet(self.tn, "")
        return
    

    def user_cc(self, argv):
        # TODO: Bug for user input "cc "
        if(argv == ""):
            magentaprint("Usage:  cc <spell> [<target> [<number>]]")
            tn.write("\n")  # TODO: Keep a prompt up to date so we can print
                            # immediately instead of sending to mud.
            return        
        elif(re.search(argv, " ")):
            [spell, target] = argv.split(" ",1)
        else:
            spell = argv
            target = ""
        
        if (self.CastThread != None and self.CastThread.is_alive()):
            magentaprint("Already had an instance... updating it")
            self.CastThread.set_spell(spell)
            self.CastThread.set_target(target)
            self.CastThread.keep_going()
        else:
            magentaprint("New instance of cc thread")
            self.CastThread = CastThread(self.Character, self.MudReaderHandler, self.tn, spell, target)
            self.CastThread.start()      


    def user_sc(self):
        self.stop_CastThread(True)
        #self.tn.write("\n")  # brings prompt back as if this command were a normal one
        send_to_telnet(self.tn, "")
        return
    
    def user_wie2(self, argv):
        magentaprint("wie2 called with argument %s" % (argv))
        #self.tn.write("wield %s\n" % (argv))
        #send_to_telnet(self.tn, "wield %s\n" % (argv))
        #self.tn.write("second %s\n" % (argv)) 
        #send_to_telnet(self.tn, "second %s\n" % (argv))
        return
    
    # COOL ABILITIES
    def user_hastec(self):        
        if ((self.CoolAbilityThread1 != None and 
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
            if (self.CoolAbilityThread1 == None or not self.CoolAbilityThread1.is_alive()):
                self.CoolAbilityThread1 = CoolAbilityThread(Haste(), self.MudReaderHandler, self.tn)
                self.CoolAbilityThread1.start()
            elif(self.CoolAbilityThread2 == None or not self.CoolAbilityThread2.is_alive()):
                self.CoolAbilityThread2 = CoolAbilityThread(Haste(), self.MudReaderHandler, self.tn)
                self.CoolAbilityThread2.start()
            else: 
                magentaprint("Error! both CoolAbilityThreads are unavailable!")

    
    def user_flee(self):
        self.stop_CastThread()
        now = time.time()
        time_remaining = max(self.Character.MOVE_WAIT - (now - self.Character.MOVE_CLK),
                             self.Character.ATTACK_WAIT - (now - self.Character.ATTACK_CLK),
                             self.Character.CAST_WAIT - (now - self.Character.CAST_CLK))
        magentaprint("Fleeing in %.1f sec ..." % time_remaining)
        first_sleep = max(time_remaining - self.Character.ATTACK_WAIT - 0.2, 0)
        second_sleep = time_remaining - first_sleep 
        time.sleep(first_sleep)

        # This sleep will allow KillThread to get one more swing in if there is time for it.
        # So we wait until time_remaining is 3 before stopping KillThread
        self.stop_KillThread()
        magentaprint("KillThread is stopped, %.1f until escape." % time_remaining)

        if(self.Character.WEAPON1 != ""):
            #self.tn.write("rm " + self.Character.WEAPON1 + "\n")
            send_to_telnet(self.tn, "rm " + self.Character.WEAPON1)
        #    WEAPON1 = ""
        if(self.Character.WEAPON2 != ""):
            #self.tn.write("rm " + self.Character.WEAPON2 + "\n")
            send_to_telnet(self.tn, "rm " + self.Character.WEAPON2)
        #    WEAPON2 = ""

        time.sleep(second_sleep)
        # Keep it simple.  Wait till ready then flee several times.  (beats
        # failed to escape)
        # TODO: Print if its more than a second... but I don't think that's
        # necessary
        #wait_for_attack_ready()
        #wait_for_cast_ready()
        
        now = time.time()
        time_remaining = max(self.Character.MOVE_WAIT - (now - self.Character.MOVE_CLK),
                             self.Character.ATTACK_WAIT - (now - self.Character.ATTACK_CLK),
                             self.Character.CAST_WAIT - (now - self.Character.CAST_CLK))
        if (time_remaining < 0):
            self.Character.MOVE_CLK = now
        else:
            magentaprint("(Python) Delaying by %.1f sec ..." % time_remaining)
            time.sleep(time_remaining)
            magentaprint("Sent.")
            self.Character.MOVE_CLK = now
            
        # Alternative is to check on MUD out for flee failures but that's not even
        # necessary!.
        # Note, it might be better in some cases just to flee once.  I think I will
        # implement "fl1" for that case.  (TODO)
        send_to_telnet(self.tn, "fl")
        send_to_telnet(self.tn, "fl")
        send_to_telnet(self.tn, "fl")

        # Put weapons back on.
        self.Character.MOVE_CLK = time.time()
        time.sleep(0.1)

        if(self.Character.WEAPON1 != ""):
            #self.tn.write("wie " + self.Character.WEAPON1 + "\n")
            send_to_telnet(self.tn, "wie " + self.Character.WEAPON1)
        if(self.Character.WEAPON2 != ""):
            #self.tn.write("seco " + self.Character.WEAPON2 + "\n")
            send_to_telnet(self.tn, "wie " + self.Character.WEAPON2)

        return    

