
from BotReactions import BotReactionWithFlag
from misc_functions import *

class Whois(BotReactionWithFlag):

    def __init__(self, mudReaderHandler, telnetHandler):
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler

    def execute(self, character_name):
        self.regexes = [character_name.title() + "\s+?(\S\S\S)\s\s([MF])\s\s\[(\d\d)\](\S+)\s+(\d+)\s+(\S+)\s" ]
        self.mudReaderHandler.register_reaction(self)
        self.telnetHandler.write("whois " + character_name)
        #self.wait_for_flag()
        self.mudReaderHandler.unregister_reaction(self)
        self.character_class = "Cle"
        self.gender = "M"
        self.level = 1
        self.title = "Enlightened Brother"
        self.age = "16"
        self.race = "Human"

    def notify(self, regex, M_obj):
        self.character_class = M_obj.group(1)
        self.gender = M_obj.group(2)
        self.level = int(M_obj.group(3))
        self.title = M_obj.group(4)
        self.age = M_obj.group(5)
        self.race = M_obj.group(6)
        try:
            magentaprint(self.character_class + " " + self.gender + " " + self.level + " " + self.title + " " + self.age + " " + self.age, False)            
        except Exception:
            magentaprint("Unable to ouput whois data", False)
        super(Whois, self).notify(regex, M_obj)
