###############################################################################
'''
Created on May 8, 2010

@author: Laurier
'''

from Exceptions import *

class Inventory(object):
    '''
    classdocs
    '''


    def __init__(self, mudReaderHandler_in, commandHandler_in, character_in):
        '''
        Constructor
        '''
        
        self.mudReaderHandler = mudReaderHandler_in
        self.commandHandler = commandHandler_in
        self.character = character_in
        
        
    def getList(self):
        
        self.commandHandler.process("i")
        
        retval = self.mudReaderHandler.wait_for_inventory_match()
        # Have mudReader use me instead of character.
        
        if(retval):
            return self.character.INVENTORY_LIST[:]
        else:
            raise TimeoutError
            


