
from BotReactions import BotReactionWithFlag
from misc_functions import *
from CharacterClass import CharacterClass

class Whois(BotReactionWithFlag):

    character_class = ""
    gender = ""
    level = 0
    title = ""
    age = 0
    race = ""

    def __init__(self, mudReaderHandler, telnetHandler, character):
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.character = character

    def execute(self, character_name):
        self.regexes = [character_name.title() + "\s+?(\S\S\S)\s\s([MF])\s\s\[(\d\d)\](\S+)\s+(\d+)\s+(\S+)\s" ]
        self.mudReaderHandler.register_reaction(self)

        self.telnetHandler.write("whois " + character_name)

    def notify(self, regex, M_obj):
        try:
            self.character_class = M_obj.group(1)
            self.gender = M_obj.group(2)
            self.level = int(M_obj.group(3))
            self.title = M_obj.group(4)
            self.age = M_obj.group(5)
            self.race = M_obj.group(6)
        except Exception:
            magentaprint("Unable to read whois data", False)

        try:
            magentaprint(self.character_class + " " + self.gender + " " + str(self.level) + " " + self.title + " " + self.age + " " + self.race, False)            

            self.character._class = CharacterClass(self.character_class, self.telnetHandler)
            self.character.gender = self.gender
            self.character.level = self.level
            self.character.title = self.title
            self.character.race = self.race
            self.character.configure_health_and_mana_variables()
            self.character.set_monster_kill_list()

            self.mudReaderHandler.unregister_reaction(self)
        
        except Exception:
            magentaprint("Unable to ouput whois data", False)

        super(Whois, self).notify(regex, M_obj)
