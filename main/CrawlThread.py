import threading
from threading import Thread
import atexit 
import time

from misc_functions import *
from CommandHandler import *
from Exceptions import *
from Database import *
from MudMap import *

class CrawlThread(threading.Thread):
    def __init__(self, character_in=None, commandHandler=None, mudReaderHandler_in=None):
        if(character_in==None and commandHandler==None and mudReaderHandler_in==None):
            return   
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.__stopping = False        
        
        self.character = character_in
        self.commandHandler = commandHandler
        self.mudReaderHandler = mudReaderHandler_in
        self.character.ACTIVELY_MAPPING = True

        atexit.register(self.stop)

        database = SqliteDatabase(databaseFile, threadlocals=True, check_same_thread=False)
        db.initialize(database)


    def stop(self):
        magentaprint("Crawl: stopping....   Urrrrrchhhchch!!")
        self.character.ACTIVELY_MAPPING = False
        self.__stopping = True


    def keep_going(self):
        self.__stopping = False


    def run(self):
        self.__stopping = False 
        
        magentaprint("CrawlThread: run()")

        # Here is where the fun begins.
        while(not self.__stopping):

            if(self.__stopping):
                break

            direction_list = self.decide_where_to_go()

            while(direction_list != [] and not self.__stopping):
                #breathe deep
                # Note that go returns a success value.  We have to be aware 
                # of what text has gone by to keep track of MONSTER_LIST
                # So since we know go was successful we know that 
                # MONSTER_LIST is good to go by now.
                if(self.go(direction_list[0])):
                    direction_list.pop(0)
                else:
                    if(self.character.GO_BLOCKING_MOB != ""):
                        #set the mob as a blocker then attack the mob
                        continue
                    elif(self.character.GO_PLEASE_WAIT):
                        continue
                    elif(self.character.GO_TIMEOUT):
                        direction_list.pop(0)
                    elif(self.character.GO_NO_EXIT):
                        direction_list.pop()
                        continue
                time.sleep(1)


    def decide_where_to_go(self):
        if (not self.character.CAN_SEE):
            magentaprint("I'm bliiiiiinnddddd!!!", False)
            self.commandHandler.process("c light")
            time.sleep(2)
            self.commandHandler.process("l")
        elif self.character.DEAD:
            time.sleep(12) #wait in Limbo
            self.character.DEAD = False
        
        time.sleep(0.5)
        curArea = Area.get_area_by_id(self.character.AREA_ID)
        curAreaExits = AreaExit.get_area_exits_from_area(curArea)
        chosen_exit = self.pick_exit(curAreaExits)
        directions = chosen_exit

        return directions

    def pick_exit(self, area_exit_list):
        #find a null exit
        for area_exit in area_exit_list:
            if (area_exit.area_to is None and area_exit.is_useable):
                return [area_exit.exit_type.name]

        #if we didn't find a null exit we end up here and the magic starts
        mud_map = MudMap()

        return mud_map.get_nearest_unexplored_path(self.character.AREA_ID)

    def go(self, exit_str):
        #time.sleep(0.8) # sometimes not a good idea to go immediately
        
        if(self.__stopping):
            return True
        
        magentaprint("Going " + str(exit_str))
        wait_for_move_ready(self.character)
        wait_for_attack_ready(self.character)
        wait_for_cast_ready(self.character)

        magentaprint(str(exit_str), False)

        if(re.match("(.*?door)", exit_str)):
            self.commandHandler.process("open " + exit_str)
            self.commandHandler.process("go " + exit_str)
            return self.mudReaderHandler.check_for_successful_go()
        else:
            self.commandHandler.process("go " + exit_str)
            return self.mudReaderHandler.check_for_successful_go()
