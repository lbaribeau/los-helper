###############################################################################

import threading
from threading import Thread
import atexit 
import time

from misc_functions import *
from CommandHandler import *
from Inventory import *
from Exceptions import *

class BotThread(threading.Thread):

    ConsoleHandler = newConsoleHandler()
    def __init__(self, starting_path, character_in, commandHandler, 
				 mudReaderHandler_in, inventory_in):   
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.__stopping = False
        
        
        self.character = character_in
        self.commandHandler = commandHandler
        self.mudReaderHandler = mudReaderHandler_in
        self.inventory = inventory_in
        
        # Set TOTALPATHS.  Setting it lower than the actual number
        # of paths in decide_where_to_go is a way to truncate paths
        # you don't want to send low level characters on.
        if(self.character.LEVEL <= 2):
            self.__TOTALPATHS = 8 # Kobolds are level 1 safe.
        elif(self.character.LEVEL <= 7):
            self.__TOTALPATHS = 10 # include hookers for level 3            
        else:
            self.__TOTALPATHS = 14 # start the fort and bandits at lvl 8
            
        if(isinstance(starting_path, int) and starting_path < self.__TOTALPATHS):
            self.__nextpath = starting_path
        else:
            self.__nextpath = 0
            
        
            
        atexit.register(self.stop)

    def stop(self):
        magentaprint("Robot: stopping....   Urrrrrchhhchch!!")
        self.__stopping = True

    def keep_going(self):
        self.__stopping = False

    def run(self):
        # Overall algorithm is:
            # rest
            # check weapons, armour
            #    go a direction
            #    (monster list up to date if go worked)
            #        engage
            #        heal, check weapons
            # Always healed while traveling.
                    
        #global MOBS_JOINED_IN
        self.__stopping = False

        # Here is where the fun begins.
        while(not self.__stopping):
            # Start of thought pattern, first check aura and rest
            self.rest()  # Note that aura is checked every time you rest.

            if(self.__stopping):
                break

            self.check_weapons()
            self.check_armour()
            
            direction_list = self.decide_where_to_go()
                # This list will contain a full route returning me to the
                # chapel at the end.
                # How will I indicate that I'm going to a shop?
                # I'll probably give a direction like "sell_everything"
                # to the 'go' function which will call some routine.
                # Then I don't have to know at this point where I'm going!

                # This also considers the current aura.  Note that it was
                # updated before we started resting.

            while(direction_list != [] and not self.__stopping):
                # Note that go returns a success value.  We have to be aware 
                # of what text has gone by to keep track of MONSTER_LIST
                # So since we know go was successful we know that 
                # MONSTER_LIST is good to go by now.
                if(self.go(direction_list[0])):
                    # Successful go.
                    direction_list.pop(0)
                    self.character.MOBS_JOINED_IN = [] 
                    self.character.MOBS_ATTACKING = []
                else:
                    # Go fails... usually something blocked exit.
                    # Also happens on timeout... which happens to me when I
                    # use the scroll bar on the command prompt window, which 
                    # suppresses output
                    
                    # Why might go fail?  
                    #  - blocking mob
                    #  - please wait 1 second
                    #  - exit doesn't exist
                    
                    # These should all be set by MudReader and unset by the 
                    # MudReaderHandler when we called check_for_successful_go.
                    if(self.character.GO_BLOCKING_MOB != ""):
                        #MUD_read_thread sets GO_BLOCKING_MOB when go returns false
                        self.begin_combat(self.character.GO_BLOCKING_MOB)
                        # Error here...  check_for_monsters will clear
                        # MONSTER_LIST at the same time as MUD_read
                        # notices that the street trader is dead and tries to
                        # remove it.
                        self.character.GO_BLOCKING_MOB = ""
                        continue  # No need to do all that other stuff
                            # if we were trying to leave and were blocked.
                            # Actually it would be buggy because MUD_thread's
                            # gonna want to remove the street trader from
                            # the list, but check_for_monsters might
                            # clear it.
                    elif(self.character.GO_PLEASE_WAIT):
                        # Just try again.
                        magentaprint("Bot: Got please wait on a go attempt, retrying.")
                        continue
                    elif(self.character.GO_TIMEOUT):
                        magentaprint("Bot: Check go timed out. I will try again, hopefully next one will work.")
                        # This can happen when the system clock makes time.time() inconsistent.
                        # Unless I can fix this I have to ignore this case and hope it worked.
                        direction_list.pop(0)
                        self.character.MOBS_JOINED_IN = [] 
                        self.character.MOBS_ATTACKING = []
                    elif(self.character.GO_NO_EXIT): 
                        # This is a tough one.  Hopefully it never 
                        # happens.  I'm gonna assume it happened 
                        # because the last go actually worked and 
                        # was wrongly determined not to.
                        direction_list.pop()
                        self.character.MOBS_JOINED_IN = []
                        self.character.MOBS_ATTACKING = []
                        continue

                # Okay, successful go.  I'm going to assume now that 
                # MONSTER_LIST is now up to date.
                
                #monster_list = mudReaderHandler.check_for_monsters()
                    # Updates and returns MONSTER_LIST (its the same reference!)
                #monster_list = self.character.MONSTER_LIST[:]

                if(self.ready_for_combat()):
                    new_target = self.decide_which_mob_to_kill(self.character.MONSTER_LIST)
                else:
                    new_target = ""
                    
                while (new_target != "" and not self.__stopping):
                    
                    #self.engage_monster(new_target)
                    #self.get_items()
                    
                    # MudReader maintains MONSTER_LIST pretty well by
                    # adding and removing.  
                    # It will not remove from MOBS_JOINED_IN nor 
                    # MOBS_ATTACKING because the three lists can contain 
                    # common mobs.  So before engaging a mob in one of the 
                    # latter two lists the bot should check that it is 
                    # still in the MONSTER_LIST.  Also be mindful of timing:
                    # MOBS_ATTACKING might not be populated as soon as the 
                    # bot enters the room - that's why they are engaged last
                    # (as a cleanup).
                    #self.engage_mobs_who_joined_in()
                    #self.engage_mobs_who_are_attacking()
                    #self.heal_up()  
                    #self.check_weapons()

                    # Can be a problem here... heal_up assumes we're
                    # not in combat and there could be something attacking.
                    # Checking if I'm in combat would need a look...
                    # There is the "Joins in the fight" message... I think
                    # that's how I will do it.
                    # MUD_read adds things to "joins in the fight" and
                    # I will check it here and if not empty I can't stop to
                    # heal up!                   
                                            
                    # Now we can reference MONSTER_LIST again.  Note that
                    # MudReader has already removed all of the mobs that we
                    # killed.  (That's in fact how we knew combat was over)
                    # The higher priority mobs were in the other lists 
                    # and will also have been removed from MONSTER_LIST
                    
                    self.begin_combat(new_target)
                    
                    if(self.ready_for_combat()):
                        new_target = self.decide_which_mob_to_kill(self.character.MONSTER_LIST)
                    else:
                        new_target = ""
    magentaprint("BotThread: finished now.")
                        
                    
                    

    def rest(self):
        # Check current health, rest if necessary.  Return when full health
        # and mana.
        # Now this also updates aura.  Checking aura is done here because
        # its more efficient...
        #   ie: you could do self.rest then self.update_aura BUT then you
        #       would be short a mana.
        #   if you did it beforehand then you have to ensure you HAVE a mana...
        #   and if you don't what do you do?  I just thought it better to do
        #   it   all here.
        
        MANA_TO_WAIT = self.character.MAX_MANA - 12
        if(self.character.BLACK_MAGIC): 
            MANA_TO_GO = self.character.MAX_MANA 
        else:
            if(self.character.MAX_MANA % 2 == 1):
                MANA_TO_GO = self.character.MAX_MANA - 1
            else:
                MANA_TO_GO = self.character.MAX_MANA

        aura_updated = False
        
        magentaprint("Inside rest.")

        # First, if we have a bit of mana first update aura (casts show aura)
        # and also heal up
        # Exception... if I'm full mana then I probably haven't fought enough
        # mobs to merit another check so it can be foregoed.
        # Another exception... try to identify the case for chars with low piety
        # where they don't want to spend thier mana pool vigging a few 
        # health back when they could have got it in one tick 
        if(self.character.MANA > 0):
            if(self.character.MANA != self.character.MAX_MANA):
                self.update_aura()
            aura_updated = True
            self.heal_up()
            
        # Get all mana back
        if(self.character.MANA < MANA_TO_WAIT):
            self.rest_for_mana()
        elif(self.character.MANA < MANA_TO_GO):
            self.wait_for_mana()
        else:
            # Here we are either at max or one off of max, just go...
            pass
            

        
        if(not aura_updated):
            # if we had no mana upon walking in we still have to do a show aura
            self.update_aura()
    
        if(self.character.LEVEL > 4):
            # Full mana, do a heal and one more wait and go.
            self.heal_up()
            self.wait_for_mana()  
        else:
            # Probably not the greatest logic but low level characters will need 
            # to gain heal other than healing up.
            self.rest_for_health()    
        return


    def rest_for_mana(self):
        MANA_SATISFIED = self.character.MAX_MANA - 1
        if(self.character.BLACK_MAGIC): 
            MANA_SATISFIED = self.character.MAX_MANA 
        else:
            MANA_SATISFIED = self.character.MAX_MANA - 1
        
        if(self.character.MANA < MANA_SATISFIED):
            self.commandHandler.process("rest")            
        while(self.character.MANA < MANA_SATISFIED and 
              not self.__stopping):
            
            # Be alert if a mob engages us
            if(self.character.MOBS_ATTACKING != []):
                self.engage_mobs_who_are_attacking()
                self.commandHandler.process("rest")
                
            time.sleep(0.1)
        return


    def wait_for_mana(self):
        # Waits for mana regen.  Issues an enter every few seconds to get the 
        # prompt.  Satisfied with max - 1.
        
        MANA_SATISFIED = self.character.MAX_MANA - 1
        if(self.character.BLACK_MAGIC): 
            MANA_SATISFIED = self.character.MAX_MANA 
        else:
            MANA_SATISFIED = self.character.MAX_MANA - 1
        
        while(self.character.MANA < MANA_SATISFIED and 
              not self.__stopping):
            time.sleep(3.5)
            
            # Be alert if a mob engages us
            if(self.character.MOBS_ATTACKING != []):
                self.engage_mobs_who_are_attacking()
                
            self.commandHandler.process('')
            time.sleep(1.2) #Wait for prompt to respond before checking MANA again.
            
        return
    
    def rest_for_health(self):

        # Copied code (bad)
        
        if(self.character.HEALTH < self.character.HEALTH_TO_HEAL):
            self.commandHandler.process("rest")            

        while(self.character.HEALTH < self.character.HEALTH_TO_HEAL and 
              not self.__stopping):            
            # Be alert if a mob engages us
            if(self.character.MOBS_ATTACKING != []):
                self.engage_mobs_who_are_attacking()
                self.commandHandler.process("rest")
                
            time.sleep(0.1)
        return


    def update_aura(self):
        
        if(self.__stopping):
            return False

        if(self.character.LEVEL != 1):

            wait_for_cast_ready(self.character)
            #tn.write("c show\n")
            self.commandHandler.user_ca('c show')
            
            self.mudReaderHandler.wait_for_aura_match()
        
        return True
    
    def heal_up(self):
        #global CastThread_inst
        
        heal_spell = "vig"
        heal_cost = 2
                
        if(self.__stopping):
            return
        
        magentaprint("Inside heal_up")
        if(self.character.HEALTH <= self.character.HEALTH_TO_HEAL and 
           self.character.MANA >= heal_cost):
            self.commandHandler.user_cc(heal_spell)  # Easiest way to start casting vig
            
        # Just wait for MUD_buffer to set HEALTH for us (above 60)
        while(self.character.HEALTH <= self.character.HEALTH_TO_HEAL and 
              self.character.MANA >= heal_cost and not self.__stopping):
            
            # Be alert if a mob engages us
            if(self.character.MOBS_ATTACKING != []):
                self.engage_mobs_who_are_attacking()
                self.commandHandler.user_cc(heal_spell)
            
            time.sleep(0.05)     

        #if(CastThread_inst != None and CastThread_inst.is_alive()):
        #    CastThread_inst.stop()
        self.commandHandler.stop_CastThread()
        
        magentaprint("Exiting heal_up")
            
        return


    def check_weapons(self):
        
        if(self.__stopping):
            return
        magentaprint("Inside check_weapons.")
        return

    def check_armour(self):
        
        if(self.__stopping):
            return
        magentaprint("Inside check_armour.")
        return

    def decide_where_to_go(self):
        magentaprint("Inside decide_where_to_go")
        # TODO Initialization is not the best place to set TOTAL PATHS...
        # Should be set here.
        
        # Paths.
        SHOP_AND_TIP_PATH = ["out", "s", "w", 'w', 'w', 's', 's', "shop",
                          "sell_items", 
                          "out", "se", 'e', 'e', 'e', 'e', "ne", "tip",
                          "drop_items",
                          "out", 'n', 'n', 'w', 'w', 'w', 'n', "chapel"]
                          #'n', 'n', 'e', 'e', 'e', 'n', "chapel"]
                          
        THEATRE_PATH = ["out", "s", "w", "w", "w", "s", "theat", "stair",
                          "cubby", "out", "down", "swing", "seat", "out",
                          "down", "seat", "out", "open door", "stage",
                          "side 2", "backstage", "door", "out", "curtain",
                          "stage", "side", "open door",
                          "up", "out", "out", "n", "e",
                          "e", "e", "n", "chapel"]
        
        MARKET_PATH = ["out", 's', 'e', 'e', 'e', 'n', 'w', 'w', 'n', 'n',
                          's', 'w', 'e', 's', 'w', 's', 'n', 'w', 'e', 'n',
                          's', 'e', 'e', "out", 's', 'w', 'w', 'w', 'n',
                          "chapel"]
        
        MILITIA_SOLDIERS_PATH = ["out", "s", "e", "s", "s", "s", "w", "gate",
                          "s", "s", "sw", "sw", "sw", "sw", "s", "s", 's',"sw", "se",
                          "s", "s", "s", "s", 's', 's', 's', 's', 's', 'w',
                          'w', 'w', 'w', 'n', 'n', 's', 's', 'e', 'e', 'e', 'e', 'n',
                          'n', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e',
                          "ne", 'e', "ne", "ne", "ne", "ne", "ne", "ne", 'n',
                          'n', 'w', 's', "sw", "ne", 'n', 'e', 'n', 'n', 'n',
                          'n', 'n', 'n', 'n', 'n', 'n', 'n', "nw", "nw", "nw",
                          "pathway", "nw", 'n', 'n', 'n', "nw", "nw",
                          'n', 'n', "gate", 'w', 'n', "nw", "nw", 'n',
                          'e', 'e', 'e', 's', 's', 's', 's', "gate", 
                          's', 's', "se", "se",
                          's', 's', 's', "se", "s", 'w', 'w', 'w', "nw",
                          "nw", 'n', "gate", 'e', 'n', 'n', 'n', 'w', 'n',
                          "chapel"]
        
        KOBOLD_PATH = ["out", 's', 'e', 's', 's', 's', 'w', "gate", 's',
                          "se", "se", 'e', 'e', 'e', "se", "se", "se", 's',
                          's', 's', 's', 's', 's', 's', 's', 's', 's', 'e',
                          "ne", 'e', 'e', 's', "glowing", "passage", "mines",
                          'd', 'n',
                          'n', 'n', 'n', "ne", 'n', 'w', 'n', 'n', 'e',
                          "open door", 'w', "gully", 'u', "boulder", 'u',
                          "cave 3", 'ne', 'ne', 'n', 's', 'u', 'e', 'se', 
                          'cave', 'out', 
                          # Note: You can remove the following line of code 
                          # to remove the kobold guards and priests fights.
                          # Priests turn you very blue.  These fights may be 
                          # difficult.
                          # Also useful to test mobs who join in.
                          #"prepare", 'e', 'ne', "door", "door", "prepare", 'sw','w',
                          "ladder", 'cave', 'out', "sw", 'w', 
                          # Comment out insane kobold (TODO: check level here)
                          # 'cave', 'out', 
                          "sw", 'se', 'nw', 'w', "out", 'd',
                          "boulder", 'd', 'd', 'e', "open door", 'w', 's', 's',
                          'e', 's', "sw", 's', 's', 's', 's', "gully",
                          "glowing", "passage", "coral", 'n', 'w', 'w', "sw",
                          'w', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n',
                          'n', "nw", "nw", "nw", 'w', 'w','w', "nw", "nw", 'n',
                          "gate", 'e', 'n', 'n', 'n', 'w', 'n', "chapel"]
        CORAL_ALLEY_PATH = ["out", "s", 'e', 's', 's', 's', 'w', 'gate',
                              's', 'se', 'se', 'e', 'e', 'e',
                              'se', 'se', 'se', 's', 's', 's', 's', 'w',
                              'alley', 's', 's', 'do', 'stai',
                              # angry hooker should be avoided unless lvl 5.
                              #'do 3', 'ou',
                              'stai', 'out', 's',
                              #'w', 'e', #for zombies
                              # noticed drunken troublemakers arrive one east
                              # not sure what safest exit is... go north.
                              # red axer lvl 2 dropped studded leather collar
                              'n', 'n', 'n', 'n',
                              'e', 'n', 'n', 'n', 'n', 'nw', 'nw', 'nw',
                              'w', 'w', 'w', 'nw', 'nw', 'n',
                              'gate', 'e', 'n', 'n', 'n', 'w', 'n', 'chapel']
        
        FORT_PATH = ["out", 'n', 'n', 'w', "gate", 'n', 'n', 'n',
                          'n', 'n', "gate", 'n', 'n', 'w', 's', 's', 'e',
                          "gate", 's', 's', 's', 's', 's', 'gate', 'e',
                          's', 's', "chapel"]
        
        NORTHERN_BANDITS_PATH = ['out', 'n', 'n', 'w', 'gate', 'n', 'n', 'n',
                          'n', 'n', 'gate', 'n', 'n', 
                          "gate", 'n',
                          "nw", "nw", "sw", "sw", "sw", "sw", 's', "sw", "sw",
                          'w', 'w', "sw", "sw", "sw", "sw", "sw", "sw", 'w',
                          'w', 'w', 'w', "nw", 'w', 'w', "nw", "sw", "nw",
                          'w', 'w', 'w', "nw", 'w', 'w', 'w', 'w',
                          "south", 's', 's', 'n', 'n', 'n',
                          'e', 'e', 'e', 'e', "se", 'e', 'e', 'e',
                          "se", "ne", "se", 'e', 'e', "se", 'e', 'e', 'e',
                          'e', "ne", "ne", "ne", "ne", "ne", "ne", 'e', 'e',
                          "ne", "ne", 'n', "ne", "ne", "ne", "ne", "se", "se",
                          's', "gate", 's', 'w', 'e', 's',
                          "gate", 's', 's', 's', 's', 's', "gate", 'e', 's',
                          's', "chapel"]
        
        PATH_TO_SKIP_WITH = [ 'out', 'chapel' ]
        
        # TODO list
        # dwarven field workers (good high level content)
        # regular field workers east of Amethyst... however exit 
        # is shut during the night.


        if(self.__nextpath % 2 == 0):
            path_to_go = SHOP_AND_TIP_PATH
        elif(self.__nextpath == 1):
            path_to_go = THEATRE_PATH
        elif(self.__nextpath == 3):
            path_to_go = MARKET_PATH 
        elif(self.__nextpath == 5):
            path_to_go = MILITIA_SOLDIERS_PATH 
        elif(self.__nextpath == 7):
            if(self.character.AURA_SCALE >= my_list_search(self.character.AURA_LIST, 'blue') or
               self.character.AURA_SCALE > my_list_search(self.character.AURA_LIST, self.character.AURA_PREFERRED)):
                magentaprint("Not going to do kobolds (aura not right)")
                path_to_go = PATH_TO_SKIP_WITH
                
                # increment so we don't go selling.
                self.__nextpath = self.__nextpath + 1
            else:
                path_to_go = KOBOLD_PATH
        elif(self.__nextpath == 9):
            # hookers ... I would avoid the drunken trouble makers, but I don't
            # quite remember where they are and don't want to go through Amber
            # Also I think it's safe enough in the dark... maybe just lvl 4 
            # there are thugs
            if(self.character.LEVEL >= 7):
                path_to_go = PATH_TO_SKIP_WITH 
                # increment so we don't go selling.
                self.__nextpath = self.__nextpath + 1
            else:            
                path_to_go = CORAL_ALLEY_PATH
        elif(self.__nextpath == 11):
            path_to_go = FORT_PATH
        elif(self.__nextpath == 13):
            # Need some evil.  Do the northern bandits.
            # Check aura first since its dangerous to go as blue
            if(self.character.AURA_SCALE >= my_list_search(self.character.AURA_LIST, 'blue') or
               self.character.AURA_SCALE > my_list_search(self.character.AURA_LIST, self.character.AURA_PREFERRED)):
                # If I'm blue or if I'm bluer than my preferred aura, don't go.
                magentaprint("Not going to do bandits (aura not right)")
                path_to_go = PATH_TO_SKIP_WITH
                self.__nextpath = self.__nextpath + 1  
                # increment so we don't go selling.
            else:
                path_to_go = NORTHERN_BANDITS_PATH
        else:
            magentaprint("Unexpected case in decide_where_to_go, nextpath==" +
                         self.__nextpath)
            path_to_go = PATH_TO_SKIP_WITH
            
        if(self.__nextpath < self.__TOTALPATHS - 1):
            self.__nextpath = self.__nextpath + 1
        else:
            self.__nextpath = 0
            
        return path_to_go
    
    
            
    def go(self, exit_str):
        #time.sleep(0.8) # sometimes not a good idea to go immediately
        wait_for_move_ready(self.character)
        wait_for_attack_ready(self.character)
        wait_for_cast_ready(self.character)
        
        if(self.__stopping):
            return True
        
        # TODO (sort of a bug).  Sometimes 'go' doesn't 'go' anywhere, 
        # like for dropping or selling or preparing, etc.  The bot's 
        # logic should be fixed to realize that its not in a new area 
        # in these instances.
        
        magentaprint("Going " + exit_str + (". %f" % (time.time() - self.character.START_TIME)))
        # "go sw" doesn't work... check for nw, ne, sw, se, and accommodate
        if(exit_str == "nw" or exit_str == "ne" or
           exit_str == "sw" or exit_str == "se" or
           exit_str == 'n' or exit_str == 'e' or
           exit_str == 's' or exit_str == 'w'):
            self.commandHandler.process(exit_str)
            return self.mudReaderHandler.check_for_successful_go() 
        elif(re.match("open ", exit_str)):
            self.commandHandler.process(exit_str)
            self.commandHandler.process("go " + exit_str.split(' ')[1])
            return self.mudReaderHandler.check_for_successful_go() 
        elif(exit_str == "prepare"):
            self.commandHandler.process(exit_str)
            return True
        elif(exit_str == "sell_items"):
            self.sell_items()
            return True
        elif(exit_str == "drop_items"):
            self.drop_items()
            return True
        else:
            self.commandHandler.process("go " + exit_str)
            return self.mudReaderHandler.check_for_successful_go()

    def sell_items(self):
        """
        Sell everything in inventory that is not in the keep list.
        (Updates character.INVENTORY_LIST)
        """
        
        if(self.__stopping):
            return

        #inv_success = self.update_inventory_list()
        #
        #if(not inv_success):
        #    magentaprint("BotThread: sell_items.  Timeout problem matching inventory")
        #    return

        #inv = self.character.INVENTORY_LIST[:] # create a copy
        try:
            inv = self.inventory.getList()
        except TimeoutError:
            magentaprint("BotThread: sell_items.  \
                Timeout problem matching inventory")
            return
                
        my_sell_list = extract_sellable_and_droppable(inv,  
            self.character.KEEP_LIST)
            # Chooses item names to evade "silver chalice" and "silver ring" collisions
            # Also does not include keepers.
        #self.__drop_list = my_sell_list[:]  # important to copy here
                                        # also note increased scope of drop list
        debug = False
        for item in my_sell_list:
            
            if(self.__stopping):
                return
            magentaprint("sell " + item)
            
            if(not debug):
                time.sleep(self.character.MINIMUM_SLEEP_BETWEEN_COMMANDS)
                self.commandHandler.process("sell " + item)
            #if(self.mudReaderHandler.check_if_item_was_sold()):  
                # function which handshakes with
                # MudReaderThread to determine
                # if an item sold.
                #self.__drop_list.remove(item)

        return 
    
# Wish list.
# In selling items, bot should:
#  be in chapel
#  check inventory
#  pick sell list
#  (then if its empty he doesn't have to go to the shop)
#  (another reason is to limit the scope of the drop list)
#  (it would be a function like
# def clean_inventory():
#     self.update_inventory()
#     sell_list = make_things_sellable()
#     drop_list = go_sell(sell_list)
#     go_drop(drop_list)
# Maybe this function can be user accessable :)
                
    
    def item_was_sold(self):

        self.character.MUD_RETURN_ITEM_SOLD = False
        self.character.SELL_CHECK_FLAG = 1
        now = time.time()
        while(self.character.SELL_CHECK_FLAG == 1 and time.time() - now < 3.0):
            time.sleep(0.05)
        magentaprint("Bot: Time for sell check was %f." % (time.time()-now))
        
        return self.character.MUD_RETURN_ITEM_SOLD    

#    def drop_items(self):

#        global SELL_LIST
        # Assume its the same sell list... not much should have changed.
        # Sell_list really shouldn't be global but whatevs.
        
#        my_sell_list = extract_sellable_and_droppable(SELL_LIST)
        # Chooses item names to evade "silver chalice" and "silver ring" collisions
#        debug = False
#        for item in my_sell_list:
#            time.sleep(0.8)
            
#            if(self.__stopping):
#                return
            
#            if(debug):
#                print "drop " + item
#            else:
#                self.commandHandler.process("drop " + item )

#        return
    def drop_items(self):
        
        # not yet set up for Inv object..
        
        if(self.__stopping):
            return
        
        try:
            inv = self.inventory.getList()
        except TimeoutError:
            magentaprint("BotThread: sell_items.  \
                Timeout problem matching inventory")
            return
        
        drop_list = extract_sellable_and_droppable(
            self.character.INVENTORY_LIST[:],
            self.character.KEEP_LIST[:])
        
        debug = False
        for item in drop_list:
        #for item in self.__drop_list:
            
            if(self.__stopping):
                return
            
            magentaprint("drop " + item)
            if(not debug):
                time.sleep(self.character.MINIMUM_SLEEP_BETWEEN_COMMANDS)
                self.commandHandler.process("drop " + item)
            
        return



#    def set_up_sell_list(self):
        # Do so by removing everything from the inventory list that is in the
        # keep list.

#        global INVENTORY_LIST
#        global SELL_LIST        



#        return

        

    
                
            
        
            
#    def decide_which_ones_to_kill(self, monster_list):
#        self.ConsoleHandler.magenta()
#        print("Inside decide_which_ones_to_kill")
#        return_list = monster_list[:] # create a copy.
#        for i in range(0, len(monster_list)):
            #if(MONSTER_KILL_LIST.find(monster_list[i]) == -1):
            #print "Before if " + str(i)
            #print monster_list
#            if(my_list_search(MONSTER_KILL_LIST, monster_list[i]) == -1):
#                print "In if " + str(i) + ".  Removing " + monster_list[i]
#                return_list.remove(monster_list[i])

#        print return_list
#        return return_list

    def decide_which_mob_to_kill(self, monster_list_in):
        magentaprint("Inside decide_which_mob_to_kill")

        monster_list = monster_list_in[:]  # make a copy in case list is volatile
        # First, make sure that we are good to go
        # Check for mana and whether there are any guards.
        #if (self.character.HEALTH < self.character.HEALTH_TO_HEAL):
        #    self.heal_up()
        #if (self.character.MANA <= self.character.MANA_TO_ENGAGE):
        #    return ""
        for mob in monster_list:
            if (re.search("town guard", mob) or re.search("town crier", mob) or
                mob == "clown"):
                return ""

        # If a mob is attacking already give that priority.
        # (Note that it's possible that a mob is angry and we don't know it yet)
        for mob in self.character.MOBS_ATTACKING:
            if(my_list_search(monster_list_in, mob) != -1):
                return mob
        
        # Return the first mob that is in the kill list
        for mob in monster_list:
            if(my_list_search(self.character.MONSTER_KILL_LIST, mob) != -1):
                return mob
            
        return ""
    

#    def decide_whether_to_engage(self, monster):

#        if(self.__stopping):
#            return
        
#        magentaprint("Inside decide_whether_to_engage")

        # Note that I've already made sure the monster is in the engage list.
        # Here I just check health & mana.  Could add more checks later if
        # necessary.
        
#        return self.character.HEALTH > self.character.HEALTH_TO_HEAL and self.character.MANA != 0

    def begin_combat(self, monster):
        """ This is a higher level function than engage_monster.
        Engage_monster handles the combat threads and exits when 
        the monster is toast.  This function calls engage monster 
        but also will additionally engage all the monsters that 
        joined in or may have begun attacking.  It also grabs the 
        items, heals up, and maintains weapons before returning to 
        the top level, simply because the bot always does that :).
        """
        self.engage_monster(monster)
        self.get_items()
        self.engage_mobs_who_joined_in()
        self.engage_mobs_who_are_attacking()
        if(not self.character.BLACK_MAGIC):
            self.heal_up()
        self.check_weapons()
        return
        


    def engage_monster(self, monster):
        
        vigor_cost = 2
        black_magic_spell_cost = 3
        
        if(self.__stopping):
            return
        
        magentaprint("Inside engage_monster... engaging " + monster)
        # Just start up kk.  Also do heals if I want.
        # Condition to stop is when kk stops for some reason.  Later (TODO) I
        # should ensure the mob is dead by chasing, however that's only
        # possible in very nice north/south environments.
        # Also TODO: Add a way to stop... however there may be no need.

        self.commandHandler.user_kk(monster)
        
        time.sleep(1)  # wait for a sec before casting magic etc. 
                        # for a couple of reasons:  so casting and attacking 
                        # are NOT in sync (not desired so that stray casts 
                        # don't go off when mob dies,) and maybe mob was one-shot.

        while(self.commandHandler.KillThread_inst != None and self.commandHandler.KillThread_inst
              and self.commandHandler.KillThread_inst.get_stopping() == False):
            # Just wait around and do stuff until the kk thread is done.
            
            if(not self.character.BLACK_MAGIC):
                # HEAL Checks
                if(self.character.HEALTH <= self.character.HEALTH_TO_HEAL):
                    if(self.character.MANA >= vigor_cost):
                        # Start healing if not already
                        if(self.commandHandler.CastThread_inst == None or not self.commandHandler.CastThread_inst.is_alive()):
                            self.commandHandler.user_cc("vig")
                    else:
                        # Stop the thread if MANA is too low.
                        # This prevents "Cannot meet the casting cost!"
                        self.commandHandler.stop_CastThread()
                else: 
                    self.commandHandler.stop_CastThread()
            else:
                # Cast black magic
                if(self.character.MANA >= black_magic_spell_cost):
                    if(self.commandHandler.CastThread_inst == None or not self.commandHandler.CastThread_inst.is_alive()):
                        self.commandHandler.user_cc(self.character.FAVOURITE_SPELL + " " + monster)
                else:
                    self.commandHandler.stop_CastThread()
                    
            # TODO: restoratives (use when vig not keeping up or low mana)
            
            # FLEE Checks
            if(self.character.HEALTH <= self.character.HEALTH_TO_FLEE):
                # We're done for!  Trust CommandHandler to get us out.  
                # It will turn around and stop the bot.
                self.stop()  # turns on stopping
                self.commandHandler.user_flee() # gets our character out!
                
            time.sleep(0.05)
                

        # Done.  Hopefully the mob is dead.
        #if(CastThread_inst != None and CastThread_inst.is_alive()):
        #    user_sc()
        self.commandHandler.stop_CastThread()    
        
        if(my_list_search(self.character.MOBS_ATTACKING, monster) != -1):
            magentaprint("Bot:engage_monster: Removing " + monster + " from MOBS_ATTACKING.")
            self.character.MOBS_ATTACKING.remove(monster)
            
        magentaprint("Leaving engage_monster") 
        
        return



    def get_items(self):
        #global PREV_COMMAND
        if(self.__stopping):
            return
        magentaprint("Inside get_items")
        self.commandHandler.process("ga")  
        return


    def engage_mobs_who_joined_in(self):
        # This function checks the global list maintainted by
        # MUD_read_thread and engages any mobs that had joined in
        # and are therefore still fighting.

        magentaprint("Inside engage_mobs_who_joined_in")
        magentaprint(self.character.MOBS_JOINED_IN)

        # Don't try to heal up first since they are already fighting!

        # Commented code: bad because more mobs can join in when 
        # fighting the currently joined in mobs.
        # Also don't think I should check weapons in a fight!
#        mobs_joined_in_copy = self.character.MOBS_JOINED_IN[:]
#        for mob in mobs_joined_in_copy:

#            self.engage_monster(mob)

#            self.character.MOBS_JOINED_IN.remove(mob)

#            self.get_items()
                    
#            self.check_weapons()

        while(self.character.MOBS_JOINED_IN != []):
            self.engage_monster(self.character.MOBS_JOINED_IN[0])
            self.character.MOBS_JOINED_IN = self.character.MOBS_JOINED_IN[1:]
            self.get_items()         
        return
    
    def engage_mobs_who_are_attacking(self):
        # MudReader not currently matching strings for mobs attacking
        
        magentaprint("Inside engage_mobs_who_are_attacking")
        magentaprint(self.character.MOBS_ATTACKING)
        
        while(self.character.MOBS_ATTACKING != []):
            self.engage_monster(self.character.MOBS_ATTACKING[0])
            # engage monster does removal on MOBS_ATTACKING list
            self.get_items()
        return
    
    def ready_for_combat(self):
        return (self.character.HEALTH > self.character.HEALTH_TO_HEAL and
                self.character.MANA >= self.character.MANA_TO_ENGAGE)

        
#                monster_list = self.check_for_monsters()
                    # This fuction should also wait a bit.
                #self.ConsoleHandler.magenta()
                #print monster_list

#                target_list = self.decide_which_ones_to_kill(monster_list)

#                while(target_list != [] and not self.__stopping):
                    # Need to check again in case I've taken damage.
#                    self.check_weapons()

#                    self.heal_up()

#                    next_monster = target_list.pop(0)
#                    decision = self.decide_whether_to_engage(next_monster)
                        # So if my character runs low, this decision point
                        # will be where he decides not to fight monsters.
                        # He will eventually just make it back to the chapel.
#                    if(decision and not self.__stopping):
#                        print "ENGAGING " + next_monster
#                        self.engage_monster(next_monster)

                        # The hard part is knowing whether I had to flee.
                        # For now, just pretend it ended well.
#                        self.get_items()

# Just thinking about changing top level...
 
# I don't like this version because mobs will leave and arrive while in
# combat.  It makes more sense to recheck list every time I enter combat...
# right?  That means doing a look between every mob.  I want to avoid the
# complication of multiple threads, I want the two threads to interact only
# via flag handshakes... so I don't want MUD_read to edit monster_list.
# How about MUD_read sets a flag when a mob arrives or leaves and I update
# monster list only when I have to?  Still doing the unnecessary look although
# not very often.  Maybe its okay to edit monster_list in the case of
# arriving mobs... and leaving mobs?  Seems like a bad idea.  However, when
# do I react to a guard arriving?  I think that I need a list that MUD_read
# will edit and I need to keep a local copy.  Hey I'm already doing it.

# Okay.  So monster_list is the local copy, and MUD_read will edit
# MONSTER_LIST relatively freely:
#   - Full update when MONSTER_CHECK_FLAG is set high by bot.
#   - one-by-one additions if monsters arrive (no flag)
# Then I can check for arrived monsters in the bot by checking if the
# lists are different.
# However, that is for later.  I wanted to make it possible to implement later
# fleeing when a guard arrives, but I won't be doing that yet.

# New approach is to keep a mob list up to date (with mob arrivals and
# departures, ideally,) and then changing logic to say, decide on WHICH
# mob to kill.  That also doubles as deciding whether to engage.  Its a
# sensible way to check for guards.
 
 
