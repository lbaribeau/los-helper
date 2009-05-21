
import threading
from threading import Thread
import atexit 
import time

from misc_functions import *
from CommandHandler import *

class BotThread(threading.Thread):

    def __init__(self, starting_path, character_inst_in, CommandHandler_in, MudReadThread_in):   # Constructor
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.__stopping = False
        self.__TOTALPATHS = 12
        #self.__TOTALPATHS = 8 # not doing kobolds for while.
        if(isinstance(starting_path, int) and starting_path < self.__TOTALPATHS):
            self.__nextpath = starting_path
        else:
            self.__nextpath = 0
        self.character_inst = character_inst_in
        self.CommandHandler_inst = CommandHandler_in
        self.MudReadThread_inst = MudReadThread_in
        atexit.register(self.stop)

    def stop(self):
        magentaprint("Robot: stopping....   Urrrrrchhhchch!!")
        self.__stopping = True

    def keep_going(self):
        self.__stopping = False

    def run(self):
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
                if(self.go(direction_list[0])):
                    direction_list.pop(0)
                    self.character_inst.MOBS_JOINED_IN = [] # this is the most sensible place to
                                        # clear this list.  (successful 'go')
                else:
                    # Go fails... usually something blocked exit.
                    # Also happens on timeout... which happens to me when I
                    # use the scroll bar on the command prompt window, which 
                    #suppresses output
                    if(self.character_inst.BLOCKING_MOB != ""):
                        #MUD_read_thread sets BLOCKING_MOB when go returns false
                        self.engage_monster(self.character_inst.BLOCKING_MOB)
                        # Error here...  check_for_monsters will clear
                        # MONSTER_LIST at the same time as MUD_read
                        # notices that the street trader is dead and tries to
                        # remove it.
                        continue  # No need to do all that other stuff
                            # if we were trying to leave and were blocked.
                            # Actually it would be buggy because MUD_thread's
                            # gonna want to remove the street trader from
                            # the list, but check_for_monsters might
                            # clear it.
                    else:
                        # assume the go check was wrong and that it was successful.
                        #direction_list.pop(0)
                        # Just try again I guess.
                        self.character_inst.MOBS_JOINED_IN = []
                        continue

                monster_list = self.check_for_monsters()
                  # Updates and returns MONSTER_LIST (its the same reference!)

                new_target = self.decide_which_mob_to_kill(monster_list)
                while (new_target != "" and not self.__stopping):
                    # Overall algorithm is:
                    # rest
                    # check weapons, armour
                    #    go a direction
                    #    get initial monster list.
                    #        engage
                    #        heal, check weapons
                    # Always healed while traveling.

                    self.engage_monster(new_target)
                    #MONSTER_LIST.remove(new_target) # Is this bad?  Should I
                        # limit access to this global thing only to MUD_read?
                        # Meh.
                        # Now the other thread will do that.
                    #monster_list.remove(new_target)

                    self.get_items()
                    
                    self.check_weapons()

                    # Can be a problem here... heal_up assumes we're
                    # not in combat and there could be something attacking.
                    # Checking if I'm in combat would need a look...
                    # There is the "Joins in the fight" message... I think
                    # that's how I will do it.
                    # MUD_read adds things to "joins in the fight" and
                    # I will check it here and if not empty I can't stop to
                    # heal up!
                    self.engage_mobs_who_joined_in()
                    
                    self.heal_up()  

                    #if(monster_list != self.character_inst.MONSTER_LIST):
                        # MUD_read must have done something, so update now.
                        # This happens when a mob arrives or leaves.
                    #    monster_list = self.character_inst.MONSTER_LIST[:]

                    new_target = self.decide_which_mob_to_kill(monster_list)

                    

                    
                

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

        #global MANA     #needed?
        #global MAX_MANA  #needed?
        
        MANA_TO_WAIT = self.character_inst.MAX_MANA - 12
        MANA_TO_GO = self.character_inst.MAX_MANA - 1

        aura_updated = False
        
        magentaprint("Inside rest.")

        # First, if we have a bit of mana first update aura (casts show aura)
        # and also heal up
        # Exception... if I'm full mana then I probably haven't fought enough
        # mobs to merit another check so it can be foregoed.
        if(self.character_inst.MANA > 0):
            if(self.character_inst.MANA != self.character_inst.MAX_MANA):
                self.update_aura()
            aura_updated = True
            self.heal_up()
            
        # Get all mana back
        if(self.character_inst.MANA < MANA_TO_WAIT):
            self.rest_for_mana()
        elif(self.character_inst.MANA < MANA_TO_GO):
            self.wait_for_mana()
        else:
            # Here we are either at max or one off of max, just go...
            pass
            

        # Full mana, do a heal and one more wait and go.
        if(not aura_updated):
            # if we had no mana upon walking in we still have to do a show aura
            self.update_aura()
    
        self.heal_up()
        self.wait_for_mana()  
        
        return

    def rest_for_mana(self):
        MANA_SATISFIED = self.character_inst.MAX_MANA - 1
        
        if(self.character_inst.MANA < MANA_SATISFIED):
            self.CommandHandler_inst.process("rest")            
        while(self.character_inst.MANA < MANA_SATISFIED and 
              not self.__stopping):
            time.sleep(0.1)
        return

    def wait_for_mana(self):
        # Waits for mana regen.  Issues an enter every few seconds to get the 
        # prompt.  Satisfied with max - 1.
        
        MANA_SATISFIED = self.character_inst.MAX_MANA - 1
        
        while(self.character_inst.MANA < MANA_SATISFIED and 
              not self.__stopping):
            time.sleep(3.5)
            self.CommandHandler_inst.process('')
            time.sleep(1.2) #Wait for prompt to respond before checking MANA again.
            
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

        #n = self.__nextpath
        if(self.__nextpath % 2 == 0):
            # Shop
            path_to_go = ["out", "s", "w", 'w', 'w', 's', 's', "shop",
                          "sell_items", 
                          "out", "se", 'e', 'e', 'e', 'e', "ne", "tip",
                          "drop_items",
                          "out", 'n', 'n', 'w', 'w', 'w', 'n', "chapel"]
                          #'n', 'n', 'e', 'e', 'e', 'n', "chapel"]
        elif(self.__nextpath == 1):
            # Theatre
            path_to_go = ["out", "s", "w", "w", "w", "s", "theat", "stair",
                          "cubby", "out", "down", "swing", "seat", "out",
                          "down", "seat", "out", "open door", "stage",
                          "side 2", "backstage", "door", "out", "curtain",
                          "stage", "side", "open door",
                          "up", "out", "out", "n", "e",
                          "e", "e", "n", "chapel"]
        elif(self.__nextpath == 3):
            # Militia Soldiers
            path_to_go = ["out", "s", "e", "s", "s", "s", "w", "gate",
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
        elif(self.__nextpath == 5):
            # Dwarven fieldworkers?  do that some other time.  Do regular
            # field workers.  Setting above to go back to chapel... Actually
            # I want to avoid areas that sometimes close for now (the farms
            # do a lot.)

            # Do the market.
            path_to_go = ["out", 's', 'e', 'e', 'e', 'n', 'w', 'w', 'n', 'n',
                          's', 'w', 'e', 's', 'w', 's', 'n', 'w', 'e', 'n',
                          's', 'e', 'e', "out", 's', 'w', 'w', 'w', 'n',
                          "chapel"]
            
        elif(self.__nextpath == 7):
            # Kobolds
            if(self.character_inst.AURA_SCALE >= my_list_search(self.character_inst.AURA_LIST, 'blue') or
               self.character_inst.AURA_SCALE > my_list_search(self.character_inst.AURA_LIST, self.character_inst.AURA_PREFERRED)):
                magentaprint("Not going to do kobolds (aura not right)")
                path_to_go = ['out', 'chapel']
                # increment so we don't go selling.
                self.__nextpath = self.__nextpath + 1
            else:
                path_to_go = ["out", 's', 'e', 's', 's', 's', 'w', "gate", 's',
                          "se", "se", 'e', 'e', 'e', "se", "se", "se", 's',
                          's', 's', 's', 's', 's', 's', 's', 's', 's', 'e',
                          "ne", 'e', 'e', 's', "glowing", "passage", "mines",
                          'd', 'n',
                          'n', 'n', 'n', "ne", 'n', 'w', 'n', 'n', 'e',
                          "open door", 'w', "gully", 'u', "boulder", 'u',
                          "cave 3", 'e', "se", "nw", "ne", "cave", "out",
                          'e', "ne", "cave", "out", "ladder", "nw", "cave",
                          "out", 'w', 'd', 'n', 's', 'u', 'e', "se", 
                          #"prepare", 'e', 'ne', "door", "door", "prepare", 'sw',
                          #'w',
                          "ladder", "sw", 'w', "sw", 'w', "out", 'd',
                          "boulder", 'd', 'd', 'e', "open door", 'w', 's', 's',
                          'e', 's', "sw", 's', 's', 's', 's', "gully",
                          "glowing", "passage", "coral", 'n', 'w', 'w', "sw",
                          'w', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n',
                          'n', "nw", "nw", "nw", 'w', 'w','w', "nw", "nw", 'n',
                          "gate", 'e', 'n', 'n', 'n', 'w', 'n', "chapel"]
                
        elif(self.__nextpath == 9):
            # Fort 
            path_to_go = ["out", 'n', 'n', 'w', "gate", 'n', 'n', 'n',
                          'n', 'n', "gate", 'n', 'n', 'w', 's', 's', 'e',
                          "gate", 's', 's', 's', 's', 's', 'gate', 'e',
                          's', 's', "chapel"]
            
        elif(self.__nextpath == 11):
            # Need some evil.  Do the northern bandits.
            # Check aura first since its dangerous to go as blue
            if(self.character_inst.AURA_SCALE >= my_list_search(self.character_inst.AURA_LIST, 'blue') or
               self.character_inst.AURA_SCALE > my_list_search(self.character_inst.AURA_LIST, self.character_inst.AURA_PREFERRED)):
                # If I'm blue or if I'm bluer than my preferred aura, don't go.
                magentaprint("Not going to do bandits (aura not right)")
                path_to_go = ['out', 'chapel']
                self.__nextpath = self.__nextpath + 1  # increment so we don't
                                                        # go selling.
                
            else:
                path_to_go = ['out', 'n', 'n', 'w', 'gate', 'n', 'n', 'n',
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
                                       
                          
                          
        
        if(self.__nextpath < self.__TOTALPATHS - 1):
            self.__nextpath = self.__nextpath + 1
        else:
            self.__nextpath = 0
            
        #print "Returning" + str(path_to_go)
        return path_to_go

    def update_aura(self):
        #global AURA
        #global AURA_CHECK_FLAG
        
        SHOW_AURA_COST = 1  # Mana

        if(self.__stopping):
            return False

        wait_for_cast_ready(self.character_inst)
        #tn.write("c show\n")
        self.CommandHandler_inst.user_ca('c show')
        
        #AURA = ""          # no need to error check at that level of detail
                            # I don't think that this function will ever fail...
                            # but even if it does I think the desired behavior
                            # is just to keep the same previous aura.
                            
        #self.character_inst.AURA_CHECK_FLAG = 1
        #now = time.time()
        #while(self.character_inst.AURA_CHECK_FLAG == 1 and time.time() - now < 0.8):
        #    time.sleep(0.05)
        
        #tn.write("cast show-aura")
        
        if(self.character_inst.MANA >= SHOW_AURA_COST):
            M_obj = self.MudReadThread_inst.MUD_output_check("You glow with a (.+?) aura\.")
            if(M_obj):
                self.character_inst.AURA = M_obj.group(1)
                self.character_inst.AURA_SCALE = my_list_search(self.character_inst.AURA_LIST, self.character_inst.AURA)
                return True
            else:
                return False
        else:
            return False

    def update_inventory_list(self):
        # not tested if he has no inventory
        # Send the 'i' command to the MUD and let MUD_read_thread get the
        # response

        #global INVENTORY_LIST
        #global INVENTORY_CHECK_FLAG
        
        if(self.__stopping):
            return
        self.CommandHandler_inst.process("i")
        self.character_inst.INVENTORY_LIST = []
        self.character_inst.INVENTORY_CHECK_FLAG = 1
        now = time.time()
        while(self.character_inst.INVENTORY_CHECK_FLAG == 1 and time.time() - now < 0.8):
            time.sleep(0.05)

        return
            
    def go(self, exit_str):
        wait_for_move_ready(self.character_inst)
        wait_for_attack_ready(self.character_inst)
        wait_for_cast_ready(self.character_inst)
        
        if(self.__stopping):
            return True
        
        # TBD (sort of a bug).  Sometimes 'go' doesn't 'go' anywhere, 
        # like for dropping or selling or preparing, etc.  The bot's 
        # logic should be fixed to realize that its not in a new area 
        # in these instances.
        
        magentaprint("Going " + exit_str)
        # "go sw" doesn't work... check for nw, ne, sw, se, and accommodate
        if(exit_str == "nw" or exit_str == "ne" or
           exit_str == "sw" or exit_str == "se" or
           exit_str == 'n' or exit_str == 'e' or
           exit_str == 's' or exit_str == 'w'):
            self.CommandHandler_inst.process(exit_str)
        elif(re.match("open ", exit_str)):
            self.CommandHandler_inst.process(exit_str)
            self.CommandHandler_inst.process("go " + exit_str.split(' ')[1])
        elif(exit_str == "prepare"):
            self.CommandHandler_inst.process(exit_str)
            return True
        elif(exit_str == "sell_items"):
            self.sell_items()
            return True
        elif(exit_str == "drop_items"):
            self.drop_items()
            return True
        else:
            self.CommandHandler_inst.process("go " + exit_str)

        # Now check if successful.
       
        return self.check_for_successful_go()

    def check_for_successful_go(self):
        # This function can be called right after going through an exit
        # to determine whether 
        #global CHECK_GO_FLAG
        #global SUCCESSFUL_GO


        magentaprint("Inside check_for_successful_go")

        self.character_inst.CHECK_GO_FLAG = 1
        self.character_inst.SUCCESSFUL_GO = False
        now = time.time()
        while(self.character_inst.CHECK_GO_FLAG == 1 and time.time() - now < 2.0 and not self.__stopping):
            time.sleep(0.05)

        magentaprint("Check for successful go, returning " + str(self.character_inst.SUCCESSFUL_GO))

        return self.character_inst.SUCCESSFUL_GO        
        

    def sell_items(self):
        """
        Sell everything in inventory list that is not in the keep list.
        Returns a list of items not sold (so they can be dropped), DROP_LIST.
        """

        #global SELL_LIST
        #global DROP_LIST

        self.update_inventory_list()

        self.character_inst.SELL_LIST = self.character_inst.INVENTORY_LIST[:] # create a copy
        
        #for item in KEEP_LIST:
        #    while(my_list_search(SELL_LIST, item) != -1):
        #        SELL_LIST.remove(item)
                
        my_sell_list = make_list_sellable(self.character_inst.SELL_LIST, self.character_inst.KEEP_LIST)
          # Chooses item names to evade "silver chalice" and "silver ring" collisions
          # Also does not include keepers.
        self.character_inst.DROP_LIST = my_sell_list[:]  # important to copy here
        debug = False
        for item in my_sell_list:
        #for i in range(0, len(my_sell_list)):
            #time.sleep(0.8)
            
            if(self.__stopping):
                return
            
            if(debug):
                magentaprint("sell " + item)
            else:
                magentaprint("sell " + item)
                self.CommandHandler_inst.process("sell " + item)

            if(self.item_was_sold()):  # function which handshakes with
                                    # MUD_read_thread to determine
                                    # if an item sold.
                self.character_inst.DROP_LIST.remove(item)

        return 

    def item_was_sold(self):
        #global SELL_CHECK_FLAG
        #global MUD_RETURN_ITEM_SOLD

        self.character_inst.MUD_RETURN_ITEM_SOLD = False
        self.character_inst.SELL_CHECK_FLAG = 1
        now = time.time()
        while(self.character_inst.SELL_CHECK_FLAG == 1 and time.time() - now < 3.0):
            time.sleep(0.05)
        
        return self.character_inst.MUD_RETURN_ITEM_SOLD    

#    def drop_items(self):

#        global SELL_LIST
        # Assume its the same sell list... not much should have changed.
        # Sell_list really shouldn't be global but whatevs.
        
#        my_sell_list = make_list_sellable(SELL_LIST)
          # Chooses item names to evade "silver chalice" and "silver ring" collisions
#        debug = False
#        for item in my_sell_list:
#            time.sleep(0.8)
            
#            if(self.__stopping):
#                return
            
#            if(debug):
#                print "drop " + item
#            else:
#                self.CommandHandler_inst.process("drop " + item )

#        return
    def drop_items(self):

        #global DROP_LIST
        # This was set up from sell_items
        

          # Chooses item names to evade "silver chalice" and "silver ring" collisions
        debug = False
        for item in self.character_inst.DROP_LIST:
            time.sleep(0.4)
            
            if(self.__stopping):
                return
            
            if(debug):
                magentaprint("drop " + item)
            else:
                magentaprint("drop " + item)
                self.CommandHandler_inst.process("drop " + item)

        return



#    def set_up_sell_list(self):
        # Do so by removing everything from the inventory list that is in the
        # keep list.

#        global INVENTORY_LIST
#        global SELL_LIST        



#        return

        

    def check_for_monsters(self):
        
        #global MONSTER_LIST
        #global MONSTER_CHECK_FLAG
        magentaprint("check_for_monsters:starting... waiting for MUD_read")
        
        self.character_inst.MONSTER_LIST = []
        self.character_inst.MONSTER_CHECK_FLAG = 1
        start_time = time.time()
        while(self.character_inst.MONSTER_CHECK_FLAG == 1 and 
              (time.time() - start_time < 1.5)):
            # Set the flag and wait for MUD_read_thread to do some magic.
            # (reminds me... TBD make bot check for MUD_read_thread life and
            # turf if necessary.
            time.sleep(0.05)    # Do a short sleep so this busy loop doesn't
                                # hog resources.
        self.character_inst.MONSTER_CHECK_FLAG = 0  # Unset flag in case it timed out.
        
        magentaprint("check_for_monsters: got the monster list, now parsing.")    
        magentaprint( self.character_inst.MONSTER_LIST)  
        
        # Now, trim the preceding "a" or "some" or "two," s well as the
        # trailing comma, and the 's' if it was plural and there's an 's'
        M_LIST = self.character_inst.MONSTER_LIST # copy the reference of the
                        # list to a variable with a shorter name
        for i in range(0, len(M_LIST)):
            #M_LIST[i].ljust(0)  # this isn't doing what I thought.
            M_LIST[i].lstrip()
            if(re.match("a ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][2:]
            elif(re.match("an ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][3:]
            elif(re.match("two ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][4:]
                if(M_LIST[i][len(M_LIST[i])-3:] == "ses"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i])-2]
                elif(M_LIST[i][len(M_LIST[i])-1] == 's'):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i])-1]
                elif(M_LIST[i][len(M_LIST[i])-8:] == "children"):
                     M_LIST[i] = M_LIST[i][0:len(M_LIST[i])-3]
                M_LIST.append(M_LIST[i])
            elif(re.match("three ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][6:]
                if(M_LIST[i][len(M_LIST[i])-3:] == "ses"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i])-2]
                elif(M_LIST[i][len(M_LIST[i])-1] == 's'):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i])-1]
                elif(M_LIST[i][len(M_LIST[i])-8:] == "children"):
                    M_LIST[i] = M_LIST[i][0:len(M_list[i])-3]
                for j in range(1, 3):
                    M_LIST.append(M_LIST[i])
            elif(re.match("four ", M_LIST[i])):
                M_LIST[i] = M_LIST[i][5:]
                if(M_LIST[i][len(M_LIST[i])-3:] == "ses"):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i])-2]
                elif(M_LIST[i][len(M_LIST[i])-1] == 's'):
                    M_LIST[i] = M_LIST[i][0:len(M_LIST[i])-1]
                elif(M_LIST[i][len(M_LIST[i])-8:] == "children"):
                    M_LIST[i] = M_LIST[i][0:len(M_list[i])-3]
                for j in range(1, 4):
                    M_LIST.append(M_LIST[i])
            commaindex = M_LIST[i].find(',')
            if(commaindex != -1):
                M_LIST = M_LIST[:commaindex]
        # I think that's it.
        
        magentaprint("Done parsing, returning list to 'run'")
        return M_LIST
        # returning it even though its global... that way
        # the caller doesn't have to fetch the global one... hopefully it isn't
        # too unintuitive.
                
            
        
            
#    def decide_which_ones_to_kill(self, monster_list):
#        ConsoleHandler.magenta()
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
        if (self.character_inst.HEALTH < self.character_inst.HEALTH_TO_HEAL):
            self.heal_up()
        if (self.character_inst.MANA <= self.character_inst.MANA_TO_ENGAGE):
            return ""
        for mob in monster_list:
            if (re.search("town guard", mob) or re.search("town crier", mob) or
                mob == "clown"):
                return ""

        # Return the first mob that is in the kill list
        for mob in monster_list:
            if(my_list_search(self.character_inst.MONSTER_KILL_LIST, mob) != -1):
                return mob
            
        return ""
            
            

    def heal_up(self):
        #global CastThread_inst

        heal_spell = "vig"
        heal_cost = 2
        
        if(self.__stopping):
            return
        
        magentaprint("Inside heal_up")
        if(self.character_inst.HEALTH <= self.character_inst.HEALTH_TO_HEAL and 
           self.character_inst.MANA >= heal_cost):
            self.CommandHandler_inst.user_cc(heal_spell)  # Easiest way to start casting vig
            
        # Just wait for MUD_buffer to set HEALTH for us (above 60)
        while(self.character_inst.HEALTH <= self.character_inst.HEALTH_TO_HEAL and 
              self.character_inst.MANA >= heal_cost and not self.__stopping):
            time.sleep(0.05)     

        #if(CastThread_inst != None and CastThread_inst.is_alive()):
        #    CastThread_inst.stop()
        self.CommandHandler_inst.stop_CastThread()
        
        magentaprint("Exiting heal_up")
            
        return

    

#    def decide_whether_to_engage(self, monster):

#        if(self.__stopping):
#            return
        
#        magentaprint("Inside decide_whether_to_engage")

        # Note that I've already made sure the monster is in the engage list.
        # Here I just check health & mana.  Could add more checks later if
        # necessary.
        
#        return self.character_inst.HEALTH > self.character_inst.HEALTH_TO_HEAL and self.character_inst.MANA != 0



    def engage_monster(self, monster):
        #global KillThread_inst
        #global CastThread_inst
        #global HEALTH
        #global HEALTH_TO_HEAL
        
        vigor_cost = 2
        if(self.__stopping):
            return
        
        magentaprint("Inside engage_monster... engaging " + monster)
        # Just start up kk.  Also do heals if I want.
        # Condition to stop is when kk stops for some reason.  Later (TBD) I
        # should ensure the mob is dead by chasing, however that's only
        # possible in very nice north/south environments.
        # Also TBD: Add a way to stop... however there may be no need.

        self.CommandHandler_inst.user_kk(monster)

        while(self.CommandHandler_inst.KillThread_inst != None and self.CommandHandler_inst.KillThread_inst
              and self.CommandHandler_inst.KillThread_inst.get_stopping() == False):
            # Just wait around and do stuff until the kk thread is done.
            
            # HEAL Checks
            if(self.character_inst.HEALTH <= self.character_inst.HEALTH_TO_HEAL):
                if(self.character_inst.MANA >= vigor_cost):
                    # Start healing if not already
                    if(self.CommandHandler_inst.CastThread_inst == None or not self.CommandHandler_inst.CastThread_inst.is_alive()):
                        self.CommandHandler_inst.user_cc("vig")
                else:
                    # Stop the thread if MANA is too low.
                    # This prevents "Cannot meet the casting cost!"
                    self.CommandHandler_inst.stop_CastThread()
            else: 
                self.CommandHandler_inst.stop_CastThread()
            
            # TBD: restoratives (use when vig not keeping up or low mana)
            
            # FLEE Checks
            if(self.character_inst.HEALTH <= self.character_inst.HEALTH_TO_FLEE):
                # We're done for!  Trust CommandHandler to get us out.  
                # It will turn around and stop the bot.
                self.stop()  # turns on stopping
                self.CommandHandler_inst.user_flee() # gets our character out!
                
            time.sleep(0.05)
                

        # Done.  Hopefully the mob is dead.
        #if(CastThread_inst != None and CastThread_inst.is_alive()):
        #    user_sc()
        self.CommandHandler_inst.stop_CastThread()     
        
        return



    def get_items(self):
        #global PREV_COMMAND
        if(self.__stopping):
            return
        magentaprint("Inside get_items")
        #PREV_COMMAND = "get all"
        #self.CommandHandler_inst.process("get all")      
        self.CommandHandler_inst.process("ga")  
        return


    def engage_mobs_who_joined_in(self):
        # This function checks the global list maintainted by
        # MUD_read_thread and engages any mobs that had joined in
        # and are therefore still fighting.
        #global MOBS_JOINED_IN

        magentaprint("Inside engage_mobs_who_joined_in")
        magentaprint(self.character_inst.MOBS_JOINED_IN)

        # Don't try to heal up first since they are already fighting!

        mobs_joined_in_copy = self.character_inst.MOBS_JOINED_IN[:]
        for mob in mobs_joined_in_copy:

            self.engage_monster(mob)

            self.character_inst.MOBS_JOINED_IN.remove(mob)

            self.get_items()
                    
            self.check_weapons()

        return

        
#                monster_list = self.check_for_monsters()
                    # This fuction should also wait a bit.
                #ConsoleHandler.magenta()
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
                 
