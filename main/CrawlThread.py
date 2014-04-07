import threading
from threading import Thread
import atexit 
import time

from misc_functions import *
from CommandHandler import *
from Exceptions import *

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
        
        magentaprint("BotThread: run()")

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
        return []