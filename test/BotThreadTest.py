import unittest
from main.bots.BotThread import *
from main.character import *
from CommandHandler import CommandHandler
from MudReaderHandler import MudReaderHandler 
        

class BotThreadTest(unittest.TestCase):
    #BotThread(character, commandHandler, mudReaderHandler, inventory, mud_map)
    def __init__(self):
        self.dummy_character = character()
        self.command_handler = CommandHandler(self.character, self.mudReaderHandler, self.telnetHandler)
