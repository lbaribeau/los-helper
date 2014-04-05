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

    def __init__(self, starting_path=None, character_in=None, commandHandler=None, 
				 mudReaderHandler_in=None, inventory_in=None):
        if(starting_path==None and character_in==None and commandHandler==None 
           and mudReaderHandler_in==None and inventory_in==None):
            return   
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

#    def _set_up_event_driven_actions(self):
#        magentaprint("Inside set_up_event_driven_actions")
#        self.mudReaderHandler.register


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
                    
        self.__stopping = False 
        
        magentaprint("BotThread: run()")
        self.set_up_automatic_ring_wearing()

        # Here is where the fun begins.
        while(not self.__stopping):
            self.rest_and_check_aura()

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
                        # MUDReaderThread sets GO_BLOCKING_MOB when go returns false
                        self.engage_monster(self.character.GO_BLOCKING_MOB)
                        self.get_items()
                        self.character.GO_BLOCKING_MOB = ""
                        self.engage_mobs_who_joined_in()
                        self.engage_any_attacking_mobs()
                        self.check_weapons()
                        if (not self.character.BLACK_MAGIC):
                            self.heal_up()
                        continue  
                            # No need to do all that other stuff
                            # if we were trying to leave and were blocked.
                            # Actually it would be buggy because MUDReaderThread
                            # will want to remove the mob from
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
                        magentaprint("Bot: Maybe it's lag... sleeping 2 sec")
                        time.sleep(2)
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

                    # Now we can reference MONSTER_LIST again.  Note that
                    # MudReader has already removed all of the mobs that we
                    # killed.  (That's in fact how we knew combat was over)
                    # The higher priority mobs were in the other lists 
                    # and will also have been removed from MONSTER_LIST
                    
                    self.engage_monster(new_target)
                    self.get_items()
                    self.engage_mobs_who_joined_in()
                    self.engage_any_attacking_mobs()
                    self.check_weapons()
                    
                    if (not self.character.BLACK_MAGIC):
                        self.heal_up()
                    
                    if(self.ready_for_combat()):
                        new_target = self.decide_which_mob_to_kill(self.character.MONSTER_LIST)
                    else:
                        new_target = ""

        magentaprint("BotThread: finished now.")
                        
    def set_up_automatic_ring_wearing(self):
        """ Makes some BotReactions so that when MudReaderHandler sees us 
        pick up a ring, we'll wear it."""
        RingReaction = GenericBotReaction("You get .+? an? .+? ring((,.+?\.)|(\.))", self.commandHandler, ["wear ring"])
        self.mudReaderHandler.register_reaction(RingReaction)
        #Todo: fix for case where there's ring mail in the inventory or multiple rings are dropped                 

    def rest_and_check_aura(self):
        magentaprint("Resting.", False)
     
        MANA_TO_WAIT = self.character.MAX_MANA - 12
        if(self.character.BLACK_MAGIC): 
            MANA_TO_GO = self.character.MAX_MANA 
        else:
            if(self.character.MAX_MANA % 2 == 1):        
                MANA_TO_GO = self.character.MAX_MANA - 1 
            else:                                        
                MANA_TO_GO = self.character.MAX_MANA     
            # We just wait for an even number because all we expect to cast is vigor.

        # TODO: Keep track of when ticks are coming and how big they'll be, and avoid vigging 
        # away all the mana for characters with low piety, whose vigors will not do much, 
        # and may just be one tick away from good health. 

        aura_updated = self.update_aura()  # Most reasonable reason to fail is if we have no mana
        self.heal_up()
            
        if(self.character.MANA < MANA_TO_WAIT):
            self.rest_for_mana()
        elif(self.character.MANA < MANA_TO_GO):
            self.wait_for_mana()
        else:
            pass
                   
        if(not aura_updated):
            self.update_aura()
    
        if(self.character.LEVEL > 4):
            self.heal_up()
            self.wait_for_mana()  
        else:
            # Probably not the greatest logic but low level characters will need 
            # to gain heal other than healing up.
            self.rest_for_health()    
        return


    def rest_for_mana(self):
        if(self.character.BLACK_MAGIC): 
            MANA_SATISFIED = self.character.MAX_MANA 
        else:
            MANA_SATISFIED = self.character.MAX_MANA - 1
        
        if(self.character.MANA < MANA_SATISFIED):
            self.commandHandler.process("rest")            

        while(self.character.MANA < MANA_SATISFIED and 
              not self.__stopping):
            
            if(self.engage_any_attacking_mobs()):
                self.commandHandler.process("rest")
                
            time.sleep(0.1)

        return


    def wait_for_mana(self):
        # Issues an enter every few seconds to get the prompt.  
        
        if(self.character.BLACK_MAGIC): 
            MANA_SATISFIED = self.character.MAX_MANA 
        else:
            MANA_SATISFIED = self.character.MAX_MANA - 1
        
        while(self.character.MANA < MANA_SATISFIED and not self.__stopping):
            time.sleep(3.5)
            self.engage_any_attacking_mobs()
            self.commandHandler.process('')
            time.sleep(1.2)  # Wait for prompt to respond before checking MANA again.
            
        return
    
    def rest_for_health(self):

        if(self.character.HEALTH >= self.character.HEALTH_TO_HEAL):
            return
            
        self.commandHandler.process("rest")            

        while(self.character.HEALTH < self.character.HEALTH_TO_HEAL and not self.__stopping):            

            if(self.engage_any_attacking_mobs()):
                self.commandHandler.process("rest")

            time.sleep(0.1)

        return


    def update_aura(self):
        magentaprint("casting show aura")
        if(self.__stopping):
            return False

        if(self.character.LEVEL < 3 or time.time() - self.character.AURA_LAST_UPDATE < 300):
            magentaprint("Not updating aura because it was recently updated (%f)." % (time.time() - self.character.AURA_LAST_UPDATE))
            return True   

        wait_for_cast_ready(self.character)
        self.commandHandler.user_ca('c show')
        aura_matched = False

        while(not aura_matched and self.character.MANA > 0): 
            self.commandHandler.user_ca('c show')
            aura_matched = self.mudReaderHandler.wait_for_aura_match() 
            
        if(aura_matched):
            self.character.AURA_LAST_UPDATE = time.time()
            return True

        return False  # Ran out of mana

    
    def heal_up(self):
        heal_spell = "vig"
        heal_cost = 2

        magentaprint("healing up")
        if(self.__stopping):
            return



        if(self.character.HEALTH <= self.character.HEALTH_TO_HEAL and 
           self.character.MANA >= heal_cost):
            if (self.character.KNOWS_VIGOR):
                self.commandHandler.user_cc(heal_spell)  
        else:
            return
        
        # Just wait for MudReader to set HEALTH for us while the cast thread continues..
        while(self.character.HEALTH <= self.character.HEALTH_TO_HEAL and not self.__stopping):
            if (self.engage_any_attacking_mobs()):
                if(self.character.MANA >= heal_cost and self.character.KNOWS_VIGOR):
                    self.commandHandler.user_cc(heal_spell)
                elif (self.character.HEALTH <= (self.character.HEALTH_TO_HEAL / 2)):
                    self.use_restorative_items()

            time.sleep(0.05)

        self.commandHandler.stop_CastThread()
        
        return

    def buff_up(self):
        if((time.time() - self.character.LAST_BUFF) > 150):
            while(self.character.MANA > 0): 
                #self.commandHandler.user_ca('c light')
                aura_matched = self.mudReaderHandler.wait_for_aura_match() 

            self.use_buff_items()
            self.character.LAST_BUFF = time.time()
            return

    def use_buff_items(self):
        if (any("steel bottle" in s for s in self.character.INVENTORY_LIST)):
            magentaprint("drinking steel bottle", False)
            self.commandHandler.process('drink bottle')
            self.character.HAS_BUFF_ITEMS = True
        else:
            self.character.HAS_BUFF_ITEMS = False
        return

    def use_restorative_items(self):
        if (self.character.HAS_RESTORE_ITEMS and any("small restorative" in s for s in self.character.INVENTORY_LIST)):
            magentaprint("drinking small restorative", False)
            self.commandHandler.process('drink restorative')
            self.character.HAS_RESTORE_ITEMS = True
        else:
            self.character.HAS_RESTORE_ITEMS = False
        return

    def check_weapons(self):
        
        if(self.__stopping):
            return

        return

    def check_armour(self):
        
        if(self.__stopping):
            return

        return

    def decide_where_to_go(self):
        magentaprint("Inside decide_where_to_go")
        
        LIMBO_TO_CHAPEL = ["ame", "out", "w", "n", "chapel"]

        SHOP_AND_TIP_PATH = ["out", "s", "w", 'w', 'w', 's', 's', "shop",
                          "sell_items", 
                          "out", "se", 'e', 'e', 'e', 'e', "ne", "tip",
                          "drop_items",
                          "out", 'n', 'n', 'w', 'w', 'w', 'n', "chapel"]
                          
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
                          # They're commented because kobolds are allowed when you're 
                          # pale blue, which is one off of blue... and these guards 
                          # and priests are dangerous unless the bot decides on his 
                          # own to engage.  Todo: check aura here (if health is 
                          # high enough,) and go in if all's good.  Even fight the 
                          # priests - because the more 'good' we can get the 
                          # more chalices we can farm.
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
        # regular field workers east of Amethyst... however exit is shut during the night.
        # loggers and sawmill operators (lots of enemies if you hang around ... perhaps add some waiting)

        if (self.character.DEAD):
            self.character.DEAD = False
            self.character.DEATHS += 1
            magentaprint("Died; Pulling up my bootstraps and starting again", False)
            path_to_go = LIMBO_TO_CHAPEL

        elif(self.__nextpath % 2 == 0):
            path_to_go = SHOP_AND_TIP_PATH

        elif(self.__nextpath == 1):
            path_to_go = THEATRE_PATH

        elif(self.__nextpath == 3):
            path_to_go = MARKET_PATH 

        elif(self.__nextpath == 5):
            path_to_go = MILITIA_SOLDIERS_PATH 

        elif(self.__nextpath == 7):
            if(self.character.AURA_SCALE < my_list_search(self.character.AURA_LIST, 'pale blue') and
               self.character.AURA_SCALE <= self.character.AURA_PREFERRED_SCALE): 
                path_to_go = KOBOLD_PATH
            else:
                magentaprint("Not going to do kobolds. Current aura, and preferred: %s,  %s" % 
                             (self.character.AURA_SCALE, self.character.AURA_PREFERRED_SCALE))
                path_to_go = PATH_TO_SKIP_WITH
                self.__nextpath = self.__nextpath + 1  # So that we don't go selling

        elif(self.__nextpath == 9):
            # hookers ... I would avoid the drunken trouble makers, but I don't
            # quite remember where they are and don't want to go through Amber
            # Also I think it's safe enough in the dark... maybe just lvl 4 
            # there are thugs
            if(self.character.LEVEL <= 6):
                path_to_go = CORAL_ALLEY_PATH
            else:            
                path_to_go = PATH_TO_SKIP_WITH 
                self.__nextpath = self.__nextpath + 1  # So that we don't go selling

        elif(self.__nextpath == 11):
            path_to_go = FORT_PATH

        elif(self.__nextpath == 13):
            if(self.character.AURA_SCALE < my_list_search(self.character.AURA_LIST, 'pale blue') or 
               self.character.AURA_SCALE <= self.character.AURA_PREFERRED_SCALE):
                path_to_go = NORTHERN_BANDITS_PATH
            else:
                magentaprint("Not going to do bandits. Current aura, and preferred: %s,  %s" % 
                             (self.character.AURA_SCALE, self.character.AURA_PREFERRED_SCALE))
                path_to_go = PATH_TO_SKIP_WITH
                self.__nextpath = self.__nextpath + 1   # So that we don't go selling

        else:
            magentaprint("Unexpected case in decide_where_to_go, nextpath==" +
                         self.__nextpath)
            path_to_go = PATH_TO_SKIP_WITH
            
        self.__nextpath = (self.__nextpath + 1) % self.__TOTALPATHS
            
        return path_to_go
    
            
    def go(self, exit_str):
        #time.sleep(0.8) # sometimes not a good idea to go immediately
        
        if(self.__stopping):
            return True
        
        # TODO (sort of a bug).  Sometimes 'go' doesn't 'go' anywhere, 
        # like for dropping or selling or preparing, etc.  The bot's 
        # logic should be fixed to realize that it's not in a new area 
        # in these instances.
        
        magentaprint("Going " + exit_str + (". %f" % (time.time() - self.character.START_TIME)))
        wait_for_move_ready(self.character)
        wait_for_attack_ready(self.character)
        wait_for_cast_ready(self.character)

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

        try:
            inv = self.inventory.getList()
        except TimeoutError:
            magentaprint("BotThread: sell_items.  \
                Timeout problem matching inventory")
            return
                
        my_sell_list = extract_sellable_and_droppable(inv, self.character.KEEP_LIST)
        magentaprint("Sell list: " + str(my_sell_list))

        for item in my_sell_list:
            
            if(self.__stopping):
                return

            time.sleep(self.character.MINIMUM_SLEEP_BETWEEN_COMMANDS)
            self.commandHandler.process("sell " + item)

            #if(self.mudReaderHandler.check_if_item_was_sold()):  
                # function which handshakes with MudReaderThread to determine if an item sold.
                #self.__drop_list.remove(item)

        return 
    
# Wish list (after graph map is done)
# In selling items, bot should:
#  be in chapel
#  check inventory for things to sell
#  (then if its empty he doesn't have to go to the shop)
# Maybe this function can be user accessable :)
    
    def item_was_sold(self):
        self.character.MUD_RETURN_ITEM_SOLD = False
        self.character.SELL_CHECK_FLAG = 1
        now = time.time()

        while(self.character.SELL_CHECK_FLAG == 1 and time.time() - now < 3.0):
            time.sleep(0.05)

        magentaprint("Bot: Time for sell check was %f." % (time.time()-now))
        return self.character.MUD_RETURN_ITEM_SOLD    


    def drop_items(self):
        
        if(self.__stopping):
            return
        
        try:
            inv = self.inventory.getList()
        except TimeoutError:
            magentaprint("BotThread: drop_items.  \
                Timeout problem matching inventory")
            return
        
        drop_list = extract_sellable_and_droppable(
            self.character.INVENTORY_LIST[:],
            self.character.KEEP_LIST[:])
        magentaprint("Drop list: " + str(drop_list))

        for item in drop_list:
            
            if(self.__stopping):
                return
            
            time.sleep(self.character.MINIMUM_SLEEP_BETWEEN_COMMANDS)
            self.commandHandler.process("drop " + item)
            
        return


    def decide_which_mob_to_kill(self, monster_list_in):
        magentaprint("Inside decide_which_mob_to_kill")
        monster_list = monster_list_in[:]

        for mob in monster_list:
            if (re.search("town guard", mob) or re.search("town crier", mob) or
                re.search("clown", mob)):
                return ""

        for mob in self.character.MOBS_ATTACKING:
            if(my_list_search(monster_list_in, mob) != -1):
                return mob
        
        for mob in monster_list:
            if(my_list_search(self.character.MONSTER_KILL_LIST, mob) != -1):
                return mob
            
        return ""
    
    def engage_monster(self, monster):
        vigor_cost = 2
        black_magic_spell_cost = 3
        
        if(self.__stopping):
            return
        
        magentaprint("Engaging " + monster)
        self.commandHandler.user_kk(monster)
        time.sleep(0.5)  # Keeps attacking and magic out of sync

        while(self.commandHandler.KillThread != None and self.commandHandler.KillThread
              and self.commandHandler.KillThread.get_stopping() == False):
            
            if(self.character.BLACK_MAGIC):
                if(self.character.MANA >= black_magic_spell_cost):
                    if(self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
                        self.commandHandler.user_cc(self.character.FAVOURITE_SPELL + " " + monster)
                else:
                    self.commandHandler.stop_CastThread()

            else:
                if(self.character.HEALTH <= self.character.HEALTH_TO_HEAL):
                    if(self.character.MANA >= vigor_cost and self.character.KNOWS_VIGOR):
                        magentaprint("healing up")
                        # Start healing if not already
                        if(self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
                            self.commandHandler.user_cc("vig")
                    else:
                        # Stop the thread if MANA is too low.
                        # This prevents "Cannot meet the casting cost!"
                        self.commandHandler.stop_CastThread()
                else: 
                    self.commandHandler.stop_CastThread()
                    
            # TODO: restoratives (use when vig not keeping up or low mana)
            if (self.character.HEALTH <= (self.character.HEALTH_TO_HEAL / 2)):
                if(self.character.MANA >= vigor_cost and self.character.KNOWS_VIGOR and
                     self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
                    self.commandHandler.user_cc(heal_spell)
                    self.commandHandler.stop_CastThread()
                else:
                    self.use_restorative_items()


            # FLEE Checks
            if(self.character.HEALTH <= self.character.HEALTH_TO_FLEE):
                # We're done for!  Trust CommandHandler to get us out.  
                # It will turn around and stop botThread.
                self.stop()  
                self.commandHandler.user_flee() 

            time.sleep(0.05)

        # OK the mob died or ran or I ran
        self.commandHandler.stop_CastThread()    
        
        if(my_list_search(self.character.MOBS_ATTACKING, monster) != -1):
            #magentaprint("Bot:engage_monster: Removing " + monster + " from MOBS_ATTACKING.")
            magentaprint("I totally just killed: " + monster, False)
            #self.character.MOBS_KILLED += 1
            self.character.MOBS_ATTACKING.remove(monster)
            
        return


    def get_items(self):
        if(self.__stopping):
            return

        self.commandHandler.process("ga")  
        return

    def engage_mobs_who_joined_in(self):
        magentaprint("Inside engage_mobs_who_joined_in")
        magentaprint(self.character.MOBS_JOINED_IN)

        while(self.character.MOBS_JOINED_IN != []):
            self.engage_monster(self.character.MOBS_JOINED_IN[0])
            self.character.MOBS_JOINED_IN = self.character.MOBS_JOINED_IN[1:]
            self.get_items()         

        return
    
    def engage_any_attacking_mobs(self):
        engaged = False

        while(self.character.MOBS_ATTACKING != []):
            engaged = True
            self.engage_monster(self.character.MOBS_ATTACKING[0])
            self.get_items()

        return engaged
    
    def ready_for_combat(self):
        return (self.character.HEALTH > self.character.HEALTH_TO_HEAL and
                self.character.MANA >= self.character.MANA_TO_ENGAGE)

        
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
 
 
