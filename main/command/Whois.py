
from reactions.BotReactions import BotReactionWithFlag
from misc_functions import *

class Whois(BotReactionWithFlag):
    good_MUD_timeout = 15.0

    def __init__(self, mudReaderHandler, telnetHandler, char):
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.char = char

    def execute(self, character_name):
        self.regexes = [character_name.title() + "\s+?(\S\S\S)\s\s([MF])\s\s\[(\d\d)\](.+?)\s+(\d+)\s+(\S+)\s" ]
        self.mudReaderHandler.register_reaction(self)
        self.telnetHandler.write("whois " + character_name)

    def notify(self, regex, M_obj):
        try:
            self.char.class_string = M_obj.group(1)
            self.char.gender = M_obj.group(2)
            self.char.level = int(M_obj.group(3))
            self.char.title = M_obj.group(4)
            self.char.age = M_obj.group(5)
            self.char.race = M_obj.group(6)
            magentaprint("Whois: " + self.char.class_string + " " + self.char.gender + " " + str(self.char.level) + " " + self.char.title + " " + self.char.age + " " + self.char.race, False)
        except Exception:
            magentaprint("Unable to read whois data", False)
        self.mudReaderHandler.unregister_reaction(self)
        super().notify(regex, M_obj)
