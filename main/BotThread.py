
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
            self.__TOTALPATHS = 20 # start the fort and bandits at lvl 8

        self.loot_threshold = 15  # the amount of loot to collect before selling

        if(isinstance(starting_path, int) and starting_path < self.__TOTALPATHS):
            self.__nextpath = starting_path
        else:
            self.__nextpath = 0
            
        atexit.register(self.stop)

#    def _set_up_event_driven_actions(self):
#        magentaprint("Inside set_up_event_driven_actions")
#        self.mudReaderHandler.register


    def stop(self):
        magentaprint("Stopping bot.", False)
        self.__stopping = True
        self.inventory.stop()  # applicable if we're selling/dropping a list


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
                        magentaprint("Bot: Check go timed out.  Could be lag.  Will try again in 7 sec.")
                        # This can happen when the system clock makes time.time() inconsistent.
                        # Unless I can fix this I have to ignore this case and hope it worked.
                        direction_list.pop(0)
                        self.character.MOBS_JOINED_IN = [] 
                        self.character.MOBS_ATTACKING = []
                        time.sleep(7)  # Bot can stop in the road randomly after lag...
                                       # I believe it's because the server registers two of the same go command
                                       # due to resending it.
                                       # There could also be slowness caused by MudReaderThread's matching.
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
        ringReaction = GenericBotReaction("(?s)You get .+? an? .+? ring((,.+?\.)|(\.))", self.commandHandler, "wear ring")
        self.mudReaderHandler.register_reaction(ringReaction)
        #Todo: fix for case where there's ring mail in the inventory or multiple rings are dropped                 

    def rest_and_check_aura(self):
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
    
        if(self.character.LEVEL > 3):
            self.heal_up()
            self.wait_for_mana()  
        else:
            # Probably not the greatest logic but low level characters will need 
            # to gain heal other than healing up.
            self.rest_for_health()

        #self.buff_up()

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
        if(self.__stopping):
            return False

        if(self.character.LEVEL < 3 or time.time() - self.character.AURA_LAST_UPDATE < 480):
            magentaprint("Last aura update: %d seconds ago." % round(time.time() - self.character.AURA_LAST_UPDATE))
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
        magentaprint("In heal_up.")
        heal_spell = "vig"
        heal_cost = 2

        if(self.__stopping):
            return

        if (self.character.TITLE == "Monk"):
            magentaprint("Last Meditate Check: " + str(time.time() - self.character.LAST_MEDITATE))
            if((time.time() - self.character.LAST_MEDITATE) > 150 and
                self.character.HEALTH <= self.character.HEALTH_TO_HEAL):
                self.commandHandler.process('meditate')
                self.character.LAST_MEDITATE = time.time()

        if(self.character.HEALTH <= self.character.HEALTH_TO_HEAL and 
           self.character.MANA >= heal_cost):
            if (self.character.KNOWS_VIGOR):
                self.commandHandler.user_cc(heal_spell)
        
        self.character.HAS_RESTORE_ITEMS = False

        # Just wait for MudReader to set HEALTH for us while the cast thread continues..
        while((self.character.HEALTH <= self.character.HEALTH_TO_HEAL and not self.__stopping) 
                and (self.character.MANA >= heal_cost or self.character.HAS_RESTORE_ITEMS) ):

            if (self.engage_any_attacking_mobs()):
                if(self.character.MANA >= heal_cost and self.character.KNOWS_VIGOR):
                    self.commandHandler.user_cc(heal_spell)
            
            #self.use_restorative_items() #spam them!!!

            time.sleep(0.05)

        self.commandHandler.stop_CastThread()
        
        return

    def buff_up(self):
        if((time.time() - self.character.LAST_BUFF) > 180):
            #while(self.character.MANA > 0): 
                #self.commandHandler.user_ca('c light')

            self.use_buff_items()
            self.character.LAST_BUFF = time.time()
            return

    def use_buff_items(self):
        #self.commandHandler.process('drink milky')
        if (any("milky potion" in s for s in self.inventory_in)):
            #magentaprint("drinking steel bottle", False)
            self.commandHandler.process('drink milky')
        else:
            self.character.HAS_BUFF_ITEMS = False
        return

    def use_restorative_items(self):
        if (any("small restorative" in s for s in self.inventory_in)):
            magentaprint("drinking small restorative", False)
            self.commandHandler.process('drink restorative')
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

        DWARVEN_FIELD_WORKERS_PATH = ['out', 'south', 'east', 'south', 'south',
                            'south', 'west', 'gate', 'south', 'southeast', 'southeast',
                            'east', 'east', 'east', 'pathway', 'northwest', 'north', 'north',
                            'north', 'southeast', 'east', 'east', 'gate', 'east', 'building',
                            'out', 'east', 'east', 'southeast', 'field', 'road', 'southeast',
                            'southeast', 'southeast', 'field', 'stile', 'stile', 'road',
                            'northwest', 'northwest', 'northwest', 'northwest', 'west', 'west',
                            'west', 'gate', 'west', 'west', 'northwest', 'south', 'south', 'south',
                            'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest',
                            'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel']

        #both gates close at night unforunately...
        FIELD_WORKERS_PATH = ['out', 'south', 'east', 'south', 'south', 'south','west',
                            'gate', 'south', 'southeast', 'southeast', 'east', 'east',
                            'east', 'pathway', 'northwest', 'north', 'north', 'north',
                            'northwest', 'northwest', 'north', 'north', 'gate', 'west',
                            'north', 'northwest', 'northwest', 'north', 'gate', 'west',
                            'west', 'southwest', 'southwest', 'west', 'west', 'west',
                            'southwest', 'southwest', 'southeast', 'southeast', 'south',
                            'gate', 'stile', 'northwest', 'southeast', 'southwest',
                            'northeast', 'stile', 'gate', 'north', 'northwest', 'northwest',
                            'west', 'west', 'gate', 'south', 'west', 'west', 'west', 'north', 'chapel']

        #Contains lvl 2&3 mobs (stacker, furniture maker, sawmill operator, mill worker) and lvl 6 mobs (sawmill / mill supervisors)
        MILL_WORKERS = ['out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate',
                        'south', 'south', 'south', 'south', 'south', 'southwest', 'south',
                        'southeast', 'southwest', 'south', 'south', 'southeast', 'south',
                        'south', 'southwest', 'bridge', 'south', 'southwest', 'west', 'canal',
                        'south', 'south', 'south', 'east', 'east', 'west', 'south', 'east',
                        'west', 'north', 'north', 'east', 'south', 'south', 'southwest', 'out',
                        'west', 'north', 'north', 'north', 'north', 'north', 'northwest',
                        'northeast', 'north', 'north', 'north', 'northeast', 'northeast',
                        'northeast', 'northeast', 'north', 'north', 'gate', 'east', 'north',
                        'north', 'north', 'west', 'north', 'chapel']

        RANCHER_SENTRY = ['out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate',
                        'south', 'southeast', 'southeast', 'east', 'east', 'east', 'pathway',
                        'northwest', 'north','north', 'north', 'northwest', 'northwest', 'north',
                        'north', 'gate', 'northeast', 'north', 'northeast', 'north', 'gate',
                        'east', 'east', 'east', 'north', 'north', 'northeast', 'north',
                        'northeast', 'gate', 'arch', 'north', 'east', 'north', 'northwest',
                        'gate', 'north', 'east', 'east', 'south', 'east', 'north', 'south',
                        'west', 'west', 'west', 'gate', 'southwest', 'south', 'east', 'south',
                        'arch', 'gate', 'southwest', 'south', 'southwest', 'south', 'south', 'west',
                        'west', 'west', 'gate', 'south', 'southwest', 'south', 'southwest', 'gate',
                        'south', 'south', 'southeast', 'southeast', 'south', 'south', 'south',
                        'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest',
                        'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel']

        PATH_TO_SKIP_WITH = [ 'out', 'chapel' ]

        if (self.character.DEAD):
            self.character.DEAD = False
            self.character.DEATHS += 1
            magentaprint("Died; Pulling up my bootstraps and starting again", False)
            return LIMBO_TO_CHAPEL

        self.__nextpath = (self.__nextpath + 1) % self.__TOTALPATHS

        if (self.__nextpath % 2 == 0):
            self.inventory.get_inventory()
            if len(self.inventory.sellable()) > self.loot_threshold:
                return SHOP_AND_TIP_PATH
            else:
                self.__nextpath = (self.__nextpath + 1) % self.__TOTALPATHS

        if(self.__nextpath == 1):
            return THEATRE_PATH

        elif(self.__nextpath == 3):
            return MARKET_PATH 

        elif(self.__nextpath == 5):
            return MILITIA_SOLDIERS_PATH 

        elif(self.__nextpath == 7):
            if self.character.AURA_SCALE < self.character.AURA_LIST.index('pale blue') and \
               self.character.AURA_SCALE <= self.character.AURA_PREFERRED_SCALE: 
                return KOBOLD_PATH
            else:
                magentaprint("Not going to do kobolds. Current aura, and preferred: %s,  %s" % 
                             (self.character.AURA_SCALE, self.character.AURA_PREFERRED_SCALE))
                self.__nextpath = self.__nextpath + 1  # So that we don't go selling
                return PATH_TO_SKIP_WITH

        elif(self.__nextpath == 9):
            # hookers ... I would avoid the drunken trouble makers, but I don't
            # quite remember where they are and don't want to go through Amber
            # Also I think it's safe enough in the dark... maybe just lvl 4 
            # there are thugs
            if(self.character.LEVEL <= 6):
                return CORAL_ALLEY_PATH
            else:            
                self.__nextpath = self.__nextpath + 1  # So that we don't go selling
                return PATH_TO_SKIP_WITH 

        elif(self.__nextpath == 11):
            return FORT_PATH

        elif(self.__nextpath == 13):
            if self.character.AURA_SCALE < self.character.AURA_LIST.index('pale blue') or \
               self.character.AURA_SCALE <= self.character.AURA_PREFERRED_SCALE:
                return NORTHERN_BANDITS_PATH
            else:
                magentaprint("Not going to do bandits. Current aura, and preferred: %s,  %s" % 
                             (self.character.AURA_SCALE, self.character.AURA_PREFERRED_SCALE))
                self.__nextpath = self.__nextpath + 1   # So that we don't go selling
                return PATH_TO_SKIP_WITH
        elif(self.__nextpath == 15):
            return DWARVEN_FIELD_WORKERS_PATH
        elif(self.__nextpath == 17):
            return MILL_WORKERS
        elif(self.__nextpath == 19):
            return RANCHER_SENTRY
        else:
            magentaprint("Unexpected case in decide_where_to_go, nextpath==" +
                         self.__nextpath)
            return PATH_TO_SKIP_WITH
        return PATH_TO_SKIP_WITH
            
            
    def go(self, exit_str):
        #time.sleep(0.8) # sometimes not a good idea to go immediately
        
        if(self.__stopping):
            return True
        
        # TODO (sort of a bug).  Sometimes 'go' doesn't 'go' anywhere, 
        # like for dropping or selling or preparing, etc.  The bot's 
        # logic should be fixed to realize that it's not in a new area 
        # in these instances.
        
        # magentaprint("Going " + exit_str + (". %d" % round(time.time() - self.character.START_TIME)))
        wait_for_move_ready(self.character)
        wait_for_attack_ready(self.character)
        wait_for_cast_ready(self.character)
        magentaprint("BotThread going " + exit_str)

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

        if(self.__stopping):
            return

        self.inventory.sell_stuff()
        
        
    def item_was_sold(self):
        self.character.MUD_RETURN_ITEM_SOLD = False
        self.character.SELL_CHECK_FLAG = 1
        now = time.time()

        while(self.character.SELL_CHECK_FLAG == 1 and time.time() - now < 3.0):
            time.sleep(0.05)

        magentaprint("Bot: Time for sell check was %.1f." % round(time.time()-now, 1))
        return self.character.MUD_RETURN_ITEM_SOLD    


    def drop_items(self):
        
        if(self.__stopping):
            return

        self.inventory.drop_stuff()

    def decide_which_mob_to_kill(self, monster_list_in):
        monster_list = monster_list_in[:]

        for mob in monster_list:
            if (re.search("town guard", mob) or re.search("town crier", mob) or
                re.search("clown", mob)):
                return ""

        for mob in self.character.MOBS_ATTACKING:
            if mob in monster_list_in:
                return mob
        
        for mob in monster_list:
            if mob in self.character.MONSTER_KILL_LIST:
                return mob
            
        return ""
    
    def engage_monster(self, monster):
        vigor_cost = 2
        black_magic_spell_cost = 3
        
        if(self.__stopping):
            return
        
        self.commandHandler.user_kk(monster)
        time.sleep(0.5)  # Keeps attacking and magic out of sync

        while(self.commandHandler.KillThread != None and self.commandHandler.KillThread
              and self.commandHandler.KillThread.stopping == False):
            
            if(self.character.BLACK_MAGIC):
                if(self.character.MANA >= black_magic_spell_cost):
                    if(self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
                        self.commandHandler.user_cc(self.character.FAVOURITE_SPELL + " " + monster)
                else:
                    self.commandHandler.stop_CastThread()
                    
            # TODO: restoratives (use when vig not keeping up or low mana)
            if (self.character.HEALTH <= (self.character.HEALTH_TO_HEAL)):
                if (self.character.TITLE == "Monk"): #meditate
                    magentaprint("Last Meditate Check: " + str(time.time() - self.character.LAST_MEDITATE))
                    if((time.time() - self.character.LAST_MEDITATE) > 150):
                        self.commandHandler.process('meditate')
                        self.character.LAST_MEDITATE = time.time()
                if(self.character.MANA >= vigor_cost and self.character.KNOWS_VIGOR and
                    self.commandHandler.CastThread == None or not self.commandHandler.CastThread.is_alive()):
                    self.commandHandler.user_cc("vig")
                    self.commandHandler.stop_CastThread()
                #else:
                    #self.use_restorative_items()


            # FLEE Checks
            if(self.character.HEALTH <= self.character.HEALTH_TO_FLEE):
                # We're done for!  Trust CommandHandler to get us out.  
                # It will turn around and stop botThread.
                self.stop()  
                self.commandHandler.user_flee() 

            time.sleep(0.05)

        # OK the mob died or ran or I ran
        self.commandHandler.stop_CastThread()    
        
        if monster in self.character.MOBS_ATTACKING:
            #magentaprint("Bot:engage_monster: Removing " + monster + " from MOBS_ATTACKING.")
            magentaprint("I believe the following is dead or gone: " + monster, False)
            self.character.MOBS_ATTACKING.remove(monster)
            
        return


    def get_items(self):
        if(self.__stopping):
            return

        self.commandHandler.process("ga")  
        return

    def engage_mobs_who_joined_in(self):
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
 
 
# You can't.  Its broken.  (Means the bot ran out of weapons.)
