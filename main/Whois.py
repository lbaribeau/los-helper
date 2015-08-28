
from BotReactions import BotReactionWithFlag
from misc_functions import *

class Whois(BotReactionWithFlag):
    good_MUD_timeout = 15.0

    def __init__(self, mudReaderHandler, telnetHandler, character):
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.character = character

    def execute(self, character_name):
        self.regexes = [character_name.title() + "\s+?(\S\S\S)\s\s([MF])\s\s\[(\d\d)\](.+?)\s+(\d+)\s+(\S+)\s" ]
        self.mudReaderHandler.register_reaction(self)
        self.telnetHandler.write("whois " + character_name)

    def notify(self, regex, M_obj):
        try:
            self.character.class_string = M_obj.group(1)
            self.character.gender = M_obj.group(2)
            self.character.level = int(M_obj.group(3))
            self.character.title = M_obj.group(4)
            self.character.age = M_obj.group(5)
            self.character.race = M_obj.group(6)
            magentaprint("Whois: " + self.character.class_string + " " + self.character.gender + " " + str(self.character.level) + " " + self.character.title + " " + self.character.age + " " + self.character.race, False)
        except Exception:
            magentaprint("Unable to read whois data", False)
        self.mudReaderHandler.unregister_reaction(self)
        super().notify(regex, M_obj)
