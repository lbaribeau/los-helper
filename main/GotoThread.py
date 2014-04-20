import threading
from threading import Thread
import atexit 
import time

from misc_functions import *
from CommandHandler import *
from Exceptions import *
from Database import *
from MudMap import *

class GotoThread(threading.Thread):
    def __init__(self, character_in=None, commandHandler=None, mudReaderHandler_in=None, database=None, mud_map=None, area_to_id=None, is_show_to=False):
        if(character_in==None and commandHandler==None and mudReaderHandler_in==None and database==None and mud_map==None and area_to_id==None):
            return   
        Thread.__init__(self)
        # Initialize some variables local to this thread
        self.__stopping = False        
        
        self.character = character_in
        self.commandHandler = commandHandler
        self.mudReaderHandler = mudReaderHandler_in

        self.database = database
        db.initialize(database)
        db.connect()
        self.mud_map = mud_map
        create_tables()
        db.close()

        if(isinstance(area_to_id, int)):
            self.area_to_id = area_to_id
            self.is_show_to = is_show_to
        else:
            magentaprint("No Area ID supplied to goto", False)

        atexit.register(self.stop)


    def stop(self):
        magentaprint("Goto: stopping....   Urrrrrchhhchch!!")
        self.__stopping = True


    def keep_going(self):
        self.__stopping = False


    def run(self):
        self.__stopping = False 
        
        magentaprint("Goto: run()")

        direction_list = self.decide_where_to_go()

        if not self.is_show_to:
            while(not self.__stopping):

                if(self.__stopping):
                    break

                while(direction_list != [] and not self.__stopping):
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
        else:
            magentaprint(str(direction_list),False)

        self.stop()


    def decide_where_to_go(self):
        directions = self.mud_map.get_path(self.character.AREA_ID, self.area_to_id)
        return directions

    def go(self, exit_str):
        #time.sleep(0.8) # sometimes not a good idea to go immediately
        
        if(self.__stopping):
            return True
        
        magentaprint("Going " + str(exit_str))
        wait_for_move_ready(self.character)
        wait_for_attack_ready(self.character)
        wait_for_cast_ready(self.character)

        if(re.match("(.*?door)", exit_str)):
            self.commandHandler.process("open " + exit_str)
            self.commandHandler.process("go " + exit_str)
            return self.mudReaderHandler.check_for_successful_go()
        else:
            self.commandHandler.process("go " + exit_str)
            return self.mudReaderHandler.check_for_successful_go()
