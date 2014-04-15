import threading
from threading import Thread
import atexit 
import time

from misc_functions import *
from CommandHandler import *
from Exceptions import *
from Cartography import *
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
            
        atexit.register(self.stop)


    def stop(self):
        magentaprint("Crawl: stopping....   Urrrrrchhhchch!!")
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
                # Note that go returns a success value.  We have to be aware 
                # of what text has gone by to keep track of MONSTER_LIST
                # So since we know go was successful we know that 
                # MONSTER_LIST is good to go by now.
                if(self.go(direction_list[0])):
                    direction_list.pop(0)
                else:
                    if(self.character.GO_BLOCKING_MOB != ""):
                        continue
                    elif(self.character.GO_PLEASE_WAIT):
                        continue
                    elif(self.character.GO_TIMEOUT):
                        direction_list.pop(0)
                        time.sleep(2)
                    elif(self.character.GO_NO_EXIT):
                        direction_list.pop()
                        continue


    def decide_where_to_go(self):
        if (not self.character.CAN_SEE):
            magentaprint("I'm bliiiiiinnddddd!!!", False)
            #cast light - wait a couple seconds and continue
        
        curArea = self.character.AREA_ID
        curAreaExits = AreaExit.get_area_exits_from_area(curArea)
        chosen_exit = self.pick_exit(curAreaExits)
        directions = [chosen_exit.name]

        return directions

    def pick_exit(self, area_exit_list):
        #find a null exit
        for area_exit in area_exit_list:
            if (area_exit.to_area is None and area_exit.is_useable):
                return area_exit

        #if we didn't find a null exit we end up here and the magic starts
        mud_map = MudMap()

        return mud_map.get_unexplored_path(self.character.AREA_ID)
