from command.Command import Command
import comm.RegexStore as R
from misc_functions import magentaprint
from db.MobMessage import MobMessage
from db.Mob import Mob
import re

class Who(Command):
    command = 'who'

    # Sample output:
    # Player          State Title                               Race          
    # -------------------------------------------------------------------------
    # Xerp            _____ Myrmidon                            Dwarf         
    # Werp            _____ Ascended One                        Dwarf         
    # Cerp            _____ Abbess                              Elf           

    # Player.+?State.+?[\n\r][\n\r]?-+[\n\r][\n\r]?
    cooldown_after_success = 0
    cooldown_after_failure = 0
    success_regexes = [
        R.who_success,
        R.player_entered,
        R.player_left,
    ]
    failure_regexes = [
    ]
    error_regexes = [
    ]

    def __init__(self, telnetHandler, character):
        super().__init__(telnetHandler)
        self.character = character

    def execute(self):
        super().execute()

    def notify(self, regex, matches):
        self.result = regex # self.success needs result to be set
        # if self.success: # Success isn't set yet
        super().notify(regex, matches)
        # if regex in R.bought:
        if regex in R.who_success:
            # for each matches print the name
            player_list = matches.group(0)
            # the first word on each line is a player name
            # regex extract all the first words
            regex = r"(\w+) .+?\n"
            player_matches = re.findall(regex, player_list)

            self.character.players = []
            for match in player_matches:
                if match == "Player":
                    continue
                self.character.players.append(match)

            magentaprint("Players: {}".format(self.character.players), False)
        elif regex in R.player_entered:
            # check if player match is in character.players list
            # if not, add it
            player_name = matches.group(1)
            if player_name not in self.character.players:
                self.character.players.append(player_name)
                magentaprint("Player joined: {}".format(player_name), False)

        elif regex in R.player_left:
            player_name = matches.group(1)
            if player_name in self.character.players:
                self.character.players.remove(player_name)
                magentaprint("Player left: {}".format(player_name), False)