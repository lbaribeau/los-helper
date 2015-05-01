
import threading
from threading import Thread
import atexit 
import time
import re

from misc_functions import magentaprint
from SmartCombat import SmartCombat
from CombatObject import Kill, Cast
from Database import *
from MudMap import *
import Command
import RegexStore
from Go import Go
from Spells import *
from Ability import *

class CommandHandler(object):
    def __init__(self, character, mudReaderHandler, telnetHandler):
        self.character = character
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.inventory = character.inventory

        self.smartCombat = SmartCombat(self.telnetHandler, Kill(telnetHandler), Cast(telnetHandler), self.character)
        # mudReaderHandler.register_reaction(self.smartCombat.kill)
        # mudReaderHandler.register_reaction(self.smartCombat.cast)
        # mudReaderHandler.register_reaction(self.smartCombat)
        self.kill = self.smartCombat.kill
        self.cast = self.smartCombat.cast
        mudReaderHandler.add_subscriber(self.kill)
        mudReaderHandler.add_subscriber(self.cast)
        self.go = Go(telnetHandler)
        mudReaderHandler.add_subscriber(self.go)
        mudReaderHandler.add_subscriber(self.smartCombat)

    def process(self, user_input):
        """ This CommandHandler function is the filter for user input that
        does some matching and calls functions based on that input.  The only
        commands that don't make it this far are 'quit', 'bot' and 'stop'.
        The reason for that is I didn't want CommandHandler to have to know
        at all about the bot, so the upper layer intercepts the relevant
        commands.  Also, when the bot is stopped on a flee, the calling layer
        handles stopping the bot."""

        the_split = user_input.split(' ')
        # user_input = the_split[0]
        arg1 = the_split[1] if len(the_split) >= 2 else None
        arg2 = the_split[2] if len(the_split) >= 3 else None
        # for a in [user_input.startswith(self.character._class.abilities.values()) for test in user_input.startswith)
        # elif any([user_input.startswith(a.command) for a in self.character._class.abilities.values()]):
        # for a in [a for a in self.character._class.abilities.values() if user_input().startswith(a.command)]
        for a in self.character._class.abilities.values():
            if the_split[0].startswith(a.command):
                if the_split[0].endswith('c'):
                    a.spam(arg1)
                else:
                    a.execute(arg1)
                return

        if user_input == 'ss':
            for a in self.character._class.abilities.values():
                a.stop()
            self.telnetHandler.write('')
        # elif re.match('ki? [a-zA-Z]|kill? [a-zA-Z]', user_input):
        elif re.match('ki? |kill?', user_input):
            self.kill.execute(target)
            # self.ki(user_input)
        elif user_input.startswith('kk '):
            self.kill.start_thread(user_input[3:].strip())
        elif user_input == 'sk' or user_input == 'skc':
            self.kill.stop()
            self.smartCombat.stop()
            self.telnetHandler.write('')
        # elif re.match('ca? [a-zA-Z]|cast? [a-zA-Z]', user_input):
        elif re.match('ca? |cast?', user_input):
            self.cast.cast(arg1, arg2)
        elif user_input.startswith('cc '):
            self.cast.start_thread(arg1, arg2)
        elif user_input == 'sc':
            self.cast.stop()
            self.smartCombat.stop_casting()
            self.telnetHandler.write('')
        elif user_input.startswith('kkc '):
            self.user_kkc(user_input[4:].strip())
        elif user_input.startswith('kk2 '):
            self.user_kk2(user_input[4:].strip())
        elif re.match('dro? ', user_input):
            self.user_dr(user_input)
        elif user_input.startswith('Sel'):
            self.inventory.sell_stuff()
        elif user_input.startswith('Dr'):
            self.inventory.drop_stuff()
        elif user_input == 'ga':
            self.telnetHandler.write('get all')
        elif user_input.startswith('go ') or re.match(str(self.character.EXIT_REGEX), user_input):
            # self.go.super_execute(user_input)
            self.user_move(user_input)
        elif self.go.is_direction(user_input):
            # self.go.super_execute(user_input)
            self.user_move(user_input)
            # routine which does appropriate waiting,
            # printing, and finally sending command.
        elif re.match('door?', user_input):
            self.go.super_execute('door')
        elif(re.match("find (.+)", user_input)):
            M_obj = re.search("find (.+)", user_input)
            magentaprint("Finding: " + str(M_obj.group(1)))
            [areas, mob_locations] = MudMap.find(str(M_obj.group(1)))

            magentaprint("Areas found:", False)
            for area in areas:
                magentaprint("<" + str(area.id) + "> - " + area.name, False)

            magentaprint("Mobs found:", False)
            for mob_location in mob_locations:
                magentaprint("<" + str(mob_location.area.id) + "> - " + mob_location.mob.name, False)
        elif re.match("wie?2 +[a-zA-Z]+( +\d+)?", user_input):
            self.user_wie2(user_input[4:].lstrip())
        elif re.match("fle?$|flee$", user_input):
            self.user_flee()
        elif re.match("HASTING", user_input):
            magentaprint(str(self.character.HASTING), False)
        elif re.match("WEAPON1", user_input):
            magentaprint(self.character.WEAPON1, False)
        elif re.match("WEAPON2", user_input):
            magentaprint(self.character.WEAPON2, False)
        elif re.match("MONSTER_CHECK_FLAG", user_input):
            magentaprint(str(self.character.MONSTER_CHECK_FLAG), False)
        elif re.match("ml", user_input): #Monster List
            magentaprint(str(self.character.MONSTER_LIST), False)
            if self.KillThread != None:
                magentaprint("Cur KT Target: " + str(self.KillThread.target), False)
            magentaprint("Mobs Attacking " + str(self.character.MOBS_ATTACKING), False)
        elif re.match("aid", user_input): #Area ID
            magentaprint("CommandHandler character.AREA_ID: " + str(self.character.AREA_ID), False)
            magentaprint("CommandHandler character.MUD_AREA: " + str(self.character.MUD_AREA), False)
        elif re.match("LAST_DIR", user_input):
            magentaprint("CommandHandler character.LAST_DIRECTION: " + str(self.character.LAST_DIRECTION), False)
        elif re.match("AREA_TITLE", user_input):
            magentaprint("CommandHandler character.AREA_TITLE: " + str(self.character.AREA_TITLE), False)
        elif re.match("EXIT_LIST", user_input):
            magentaprint(str(self.character.EXIT_LIST), False)
        elif re.match("hp", user_input):
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
            magentaprint("Kills this Session: " + str(kills), False)
        elif re.match("DUMP", user_input):
            for attr in self.character.__dict__:
                magentaprint(str(attr) + " : " + str(self.character.__dict__[attr]), False)
        elif re.match("CECHO", user_input):
            self.telnetHandler.echoing = not self.telnetHandler.echoing
        elif re.match("VERSION", user_input):
            magentaprint("Version: " + str(misc_functions.VERSION), False)
            magentaprint(self.character.__dict__, False)
        elif re.match("REPORT", user_input):
            # self.process("info")
            # time.sleep(1)
            exp = self.character.TOTAL_EXPERIENCE
            gold = self.character.TOTAL_GOLD
            aura = str(self.character.AURA)
            magentaprint("Current Aura: " + aura, False)
            magentaprint("Total EXP: " + str(exp) + " | Total Gold: " + str(gold), False)
            exp = self.character.EXPERIENCE
            expm = str(calculate_vpm(exp))
            magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, False)
            kills = len(self.character.MOBS_KILLED)
            kpm = str(calculate_vpm(kills))
            magentaprint("Kills this Session: " + str(kills) + " | Kills / MIN: " + kpm, False)
            hits_dealt = self.character.HITS_DEALT
            hits_missed = self.character.HITS_MISSED
            damage_dealt = self.character.DAMAGE_DEALT
            total_phys_attacks = hits_dealt + hits_missed
            crits_landed = self.character.CRITS_LANDED
            spells_cast = self.character.SPELLS_CAST
            spells_failed = self.character.SPELLS_FAILED
            spells_hit = spells_cast - spells_failed
            spell_damage_dealt = self.character.SPELL_DAMAGE_DEALT

            try:
                average_phys_damage = round(damage_dealt / hits_dealt, 2)
                phys_hit_rate = round(hits_dealt / total_phys_attacks * 100, 2)
                phys_crit_rate = round(crits_landed / total_phys_attacks * 100, 2)
                
                average_spell_damage = round(spell_damage_dealt / spells_hit)
                spell_hit_rate = round(spells_hit / spells_cast * 100, 2)
                spell_crit_rate = 0
            except Exception:
                average_phys_damage = -1
                average_spell_damage = -1
                phys_hit_rate = -1
                spell_hit_rate = -1
                phys_crit_rate = -1
                spell_crit_rate = -1

            magentaprint("Average Phys Damage: " + str(average_phys_damage) + " | Average Spell Damage: " + str(average_spell_damage), False)
            magentaprint("Phys Hit Rate: " + str(phys_hit_rate) + "% | Spell Hit Rate: " + str(spell_hit_rate) + "%", False)
            magentaprint("Phys Crit Rate: " + str(phys_crit_rate) + " | Spell Crit Rate: " + str(spell_crit_rate) + "%", False)
            runtime = round(get_runtime_in_minutes(), 2)
            magentaprint("Minutes Run: " + str(runtime), False)
        elif re.match("MOBS_JOINED_IN", user_input):
            magentaprint(self.character.MOBS_JOINED_IN, False)
        elif re.match("AURA", user_input):
            magentaprint(str(self.character.AURA), False)        
        elif re.match("MOBS_ATTACKING", user_input):
            magentaprint(self.character.MOBS_ATTACKING, False)
        elif re.match("MONSTER_KILL_LIST", user_input):
            magentaprint(str(self.character.MONSTER_KILL_LIST), False)
        elif re.match("reactionlist", user_input):
            for r in self.mudReaderHandler.MudReaderThread.BotReactionList:
                magentaprint('    ' + str(r), False)
        elif re.match("cackle", user_input):
            misc_functions.verboseMode = not misc_functions.verboseMode
            magentaprint("Verbose mode changed", False)
        elif re.match("defecate", user_input):
            misc_functions.debugMode = not misc_functions.debugMode
            magentaprint("Debug Mode changed", False)
        elif re.match(str(self.character.EXIT_REGEX), user_input):
            self.user_move("go " + self.character.LAST_DIRECTION)
            magentaprint("Running go on EXIT_REGEX: " + str(self.character.EXIT_REGEX), False)
        else: # Doesn't match any command we are looking for
            self.telnetHandler.write(user_input) # Just shovel to telnet.

    def ki(self, user_input):
        self.kill.execute(user_input.split(" ")[1])

    def kk(self, target):
        # self.kill.engage(self.telnetHandler, user_input[3:])
        self.kill.start_thread(target)

    def user_move(self, user_input):
        # if user_input.startswith("go "):
        #     exit = user_input.split(" ")[1]
        #     if exit == "nw":
        #         user_input = "nw"
        #     elif exit == "sw":
        #         user_input = "sw"
        #     elif exit == "ne":
        #         user_input = "ne"
        #     elif exit == "se":
        #         user_input = "se"

        self.character.TRYING_TO_MOVE = True
        self.character.LAST_DIRECTION = user_input.replace("go ", "")
        self.kill.stop()
        self.cast.stop()
        now = time.time()
        wait_from_move = self.character.MOVE_WAIT - (now - self.character.MOVE_CLK)
        time_remaining = max(wait_from_move, self.kill.wait_time(), self.cast.wait_time(), 0);
        # magentaprint("user_move: MOVE wait time: %.2f" % round(wait_from_move, 2))
        # magentaprint("user_move: kill.wait_time(): " + str(self.kill.wait_time()))
        # magentaprint("user_move: cast.wait_time(): " + str(self.cast.wait_time()))

        if time_remaining < 3.0:
            time.sleep(time_remaining)
            self.character.MOVE_CLK = now
            # self.telnetHandler.write(user_input)
            # self.go.super_execute(self.character.LAST_DIRECTION)
            self.go.execute(self.character.LAST_DIRECTION)
        else:
            magentaprint("Wait %.1f more seconds." % time_remaining)

        # elif time_remaining < 1.0:
        #     magentaprint("(Python) Delaying by %.1f sec ..." % time_remaining)
        #     time.sleep(time_remaining)
        #     magentaprint("Sent.")
        #     self.character.MOVE_CLK = now
        #     self.telnetHandler.write(user_input)
        # else:
        
    def user_dr(self, user_input):
        [command, item] = user_input.split(" ", 1)
        user_input = "drop " + item
        self.telnetHandler.write(user_input)
    
    # Commented: user_kk is deprecated and this code also doesn't work
    def user_kk(self, monster):
        magentaprint("CommandHandler.telnetHandler: " + str(self.telnetHandler))
        # self.kill.engage(self.telnetHandler, argv[3:].lstrip())
        # self.kill.engage(self.telnetHandler, monster)
        self.kill.start_thread(monster)

        # if self.KillThread != None and self.KillThread.is_alive():
        #     self.KillThread.set_target(argv)
        #     self.KillThread.keep_going()
        # else:
        #     self.KillThread = KillThread(self.character, self.mudReaderHandler, self.telnetHandler, argv)
        #     self.KillThread.start()
    
    def user_sk(self):
        self.kill.stop()
        self.smartCombat.stop()
        # self.telnetHandler.write("")

    def user_cc(self, argv):
        # TODO: Bug for user input "cc "
        if argv == "":
            magentaprint("Usage:  cc <spell> [<target> [<number>]]")
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
            self.CastThread = CastThread(self.character, 
                                         self.mudReaderHandler, 
                                         self.telnetHandler, 
                                         spell, 
                                         target)
            self.CastThread.start()      

    def user_kkc(self, argv):
        theSplit = argv.split(" ")
        n = len(theSplit)

        if argv == None or n == 1 and theSplit[0] == "":
            magentaprint("Usage:  kkc [<spell>] <target> [<number>]")
            self.telnetHandler.write("")  # TODO: Keep a prompt up to date so we can print
                                          # immediately instead of sending to mud.
        # elif n == 1 and theSplit[0] not == "":
        elif n == 1:
            spell = None
            target = theSplit[0]
        elif n == 2 and re.match("^\d+$", theSplit[1]):
            spell = None
            target = theSplit[0] + " " + theSplit[1]
        elif n == 2:
            spell = theSplit[0]
            target = theSplit[1]
        else:
            spell = theSplit[0]
            target = theSplit[1] + " " + " ".join(theSplit[2:])

        self.smartCombat.start_thread(target, spell)

        # if self.smartCombatThread != None and self.smartCombatThread.is_alive():
        #     magentaprint("CommandHandler calling smartCombatThread.keep_going()")
        #     self.smartCombatThread.set_target(argv)
        #     self.smartCombatThread.keep_going()
        # else:
        #     magentaprint("CommandHandler making new smartCombatThread")
        #     self.smartCombatThread = SmartCombat(self.character, self.mudReaderHandler, 
        #                                          self.telnetHandler, self.inventory)
        #     self.smartCombatThread.target = target  
        #     # I want to start doing threads without inheritance...
        #     self.smartCombatThread.start()

    def user_kk2(self, argv):
        # Usage: "kk2 target"
        # Uses smart combat with level 2 spell
        teh_split = argv.split(" ")
        self.user_kkc(" ".join(teh_split))
        if self.smartCombat.favourite_spell is burn:
            teh_split.insert(0, fireball)
        elif self.smartCombat.favourite_spell is hurt:
            teh_split.insert(0, dustgust)
        elif self.smartCombat.favourite_spell is blister:
            teh_split.insert(0, waterbolt)
        elif self.smartCombat.favourite_spell is rumble:
            teh_split.insert(0, crush)
        self.user_kkc(" ".join(teh_split))

    def user_sc(self):
        # self.stop_CastThread()
        self.cast.stop()
        self.smartCombat.stop_casting()
        self.telnetHandler.write("")

    def user_wie2(self, argv):
        self.telnetHandler.write("wield %s\n" % (argv))
        self.telnetHandler.write("second %s\n" % (argv))

    def user_hastec(self):        
        magentaprint("CommandHandler: user_hastec")
    
    def user_flee(self):
        self.cast.stop()
        # self.smartCombat.flee()
        now = time.time()
        time_remaining = max(self.character.MOVE_WAIT - (now - self.character.MOVE_CLK),
                             self.kill.wait_time(), self.cast.wait_time())
        self.cast.stop()
        self.smartCombat.stop_casting()
        # self.kill.start_thread(self.smartCombat.target)  # if smartCombat.thread.is_alive()
        magentaprint("Fleeing in %.1f sec ..." % time_remaining)
        first_sleep = max(time_remaining - self.kill.cooldown_after_success - 0.2, 0)
        second_sleep = time_remaining - first_sleep 
        time.sleep(first_sleep)

        # This sleep will allow KillThread to get one more swing in if there is time for it.
        # So we wait until time_remaining is 3 before stopping KillThread
        self.smartCombat.stop()
        self.kill.stop()
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
                             self.kill.wait_time(), self.cast.wait_time())
        self.character.MOVE_CLK = now
            
        # Note: in very few rare cases it may be better to flee once.  
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")
        magentaprint("Sent.", False)

        time.sleep(0.1)  

        if self.character.WEAPON1 != "":
            self.telnetHandler.write("wie " + self.character.WEAPON1)
        if self.character.WEAPON2 != "":
            self.telnetHandler.write("seco " + self.character.WEAPON2)

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
