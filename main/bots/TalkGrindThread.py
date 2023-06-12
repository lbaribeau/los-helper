import random

from misc_functions import *
from bots.BotThread import *
from db.Database import *
from db.MudMap import *
from mini_bots.travel_bot import TravelBot
from db.MobMessage import *
from db.Mob import *

# bot that finds named mobs and talks to them
class TalkGrindThread(BotThread):
      def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
            mud_map=None):
            super().__init__(character, command_handler, mud_reader_handler, mud_map)

            # self.travel_bot = TravelBot(self.char, self.command_handler, mud_map)
            self.talking = False
            self.current_topics = []
            self.target_mobs = [
                  # "Dr'Tel's Ghost",
                  # "Gerdevarashimora",
                  # "Farside",
                  # "Dwar",
                  # "Maco Bail", # Behind locked door
                  "Mayor Demlin",
                  "Commander Rilmenson",
                  "Madame Zara",
                  "Ringmaster",
                  "Farmer Malbon",
                  "Priestly Ghost",
                  "Farmer Calmor",
                  "Farmer McDermott",
                  "Farmer Grangers Ghost",
                  # # "Druid Tutor", #buggy
                  # "Bertram Dalrum",
                  # "Dame Brethil",
                  # "Douvan", "Queen Dalla", 
                  # "Jerrek", "Tag", "Rag",
                  # "Thomas Ironheart",
                  # "Olarma",
                  # "Master of Ceremonies", 
                  "Boris Ironfounder", "Tendrurn",
                  "Brotain","Rimark",
                  "Aldo","Horbuk",
                  # "Volman the Inhumer",
                  # "The Master Artificer",
                  # "Kin'Tal",
                  # "The Archbishop",
                  "Tardan",
                  # "Trantas", #hardcore arena NPC
                  "Gregor",
                  "Farmer Viladin",
                  "Cal the Hermit",
                  "Rancher Renstone",
                  "Rancher Plover",
                  "Annette Plover",
                  #"White Mage",
                  # "The Barding Lord",
                  # "Knight Errant",
                  "Lord Tamaran", "Tario", "Lady Denlise", 
                  "Vickie",
                  "Matriarch Sara",
                  "Lord Arduis","Lady Arielle","Lady Jenlira", 
                  "Corien", "Lyron the Elder","Shaldena the Red","Garbo the Hobbit","Whiteblade the Barbarian",
                  # "Great Druid",
                  # "Teamleader Egan",
                  # "Trent the Merchant",
                  "Grand Master Yang-Shi",
                  # # "Sensei",
                  "Dojo Administrator",
                  "Al'Sik the Carver",
                  "Zi'Cab the Chieftan",
                  "Vas'Polu the HawkMaster","Byr'Ula the Smith","Ha'Chans the Shaman",
                  "Th'kit the HorseMaster",
                  # "Forest Master",
                  "Broad Leaf", "Red Crown",
                  "Esrhae",
                  "Haelyn",
                  "Caethrodyn",
                  "Robar Greybeard",
                  "Greenbough the Dryad",
                  # "Deep Root",
                  "Oakheart",
                  "Winter's Watcher",
                  "Agguedian's Simulcrum",
                  # "barbarian shaman",
                  # "Cheryn",
                  "Manic Soothsayer",
                  "Elder Barthrodue",
                  "Goourd",
                  # "GuildMaster Cuvelas",
                  "Chiaru Maradiu",
                  "Thereze",
                  "Qimoth",
                  "Joffi the Mystic",
                  "Gorban",
                  "Pansy",
                  "Kelluran",
                  "Ordaran the White",
                  # "Corellan"
            ]

            self.index = 0

            self.talk_topics = [
                  "", # empty string to talk to the mob
                  # activities
                  "quest",
                  "trouble",
                  "reward",
                  "help",
                  "advice",
                  "task",
                  "mission",
                  "job",
                  "work",
                  "adventure",
                  "explore",
                  "battle",
                  "fear",
                  "danger",
                  "trade",
                  "barter",
                  "rumour",
                  "gossip",
                  # "haggle",
                  "buy",
                  "sell",
                  "purchase",
                  "exchange",
                  "offer",
                  "conjunction",
                  "invoke",
                  # leveling
                  "train",
                  # mobs
                  "griffon",
                  "ogre",
                  "giant",
                  "golem",
                  "goblin",
                  "troll",
                  "orc",
                  "dragon",
                  "wyvern",
                  "zombie",
                  "undead",
                  "kobold",
                  "spider",
                  "bandit",
                  "chameleon",
                  "bugbear",
                  "efreet",
                  "demon",
                  "demons",
                  "jaguar",
                  # things
                  "item",
                  "glade",
                  "portal",
                  "artifact",
                  "flute",
                  "mithril",
                  "adamantine",
                  "key",
                  "ore",
                  "gold",
                  "silver",
                  "copper",
                  "iron",
                  "steel",
                  "weapon",
                  "spell",
                  "armor",
                  "treasure",
                  "gem",
                  "fire",
                  "water",
                  "earth",
                  "air",
                  "wind",
                  "good",
                  "evil",
                  "dark",
                  "light",
                  "rod",
                  "ruin",
                  "song",
                  "potion",
                  "ingredient",
                  "rune",
                  "sigil",
                  "charm",
                  # spells
                  "blind",
                  "clairvoyance",
                  "invisibility",
                  "levitate",
                  "fly",
                  "heal",
                  "poison",
                  "disease",
                  "curse",
                  "bless",
                  "cure",
                  "protect",
                  "scroll",
                  "wand",
                  "resist",
                  "restore",
                  "reveal",
                  "silence",
                  "transport",
                  "word-of-recall",
                  "sealing",
                  # places
                  "mine",
                  "cave",
                  "deep",
                  "dark",
                  "forest",
                  "mountain",
                  "dungeon",
                  "castle",
                  "tower",
                  "bog",
                  "swamp",
                  "station",
                  "inn",
                  "tavern",
                  "guild",
                  "chapel",
                  "shop",
                  "farm",
                  "lair",
                  "nest",
                  "Amber",
                  "HighMarket",
                  "Amethyst",
                  "Farrin",
                  "Coral",
                  "Kelim",
                  "Blackstar",
                  "Halwyn",
                  "Rook",
                  "astral",
                  "elemental",
                  "plane",
                  "entrance",
                  "ahinma",
                  "ulwyne",
                  "blood",
                  "ranch",
                  "monolith",
                  "shrine",
                  "divide",
                  "great",
                  "blasted",
                  "plains",
                  "fens",
                  "desert",
                  #races
                  "dwarf",
                  "elf",
                  "human",
                  "orc",
                  "hobbit",
                  "gnome",
                  "half",
                  "ent",
                  "dryad",
                  # classes
                  "fighter",
                  "warrior",
                  "barbarian",
                  "mage",
                  "cleric",
                  "thief",
                  "ranger",
                  "knight",
                  "assassin",
                  "dark-knight",
                  "bard",
                  "alchemist",
                  "druid",
                  # characters
                  "deldan",
                  "lord",
                  "lady",
                  "ongrak",
                  "zuthra",
                  "ashkavan",
                  "jooma",
                  "aaashaaal",
                  "prem",
                  "feleessa",
                  "phoenix",
                  "granger",
                  "renstone",
                  "plover",
            ]

      def get_path_to_target_mob(self, mob):
            # find a mob to talk to
            mob_location = MudMap.get_mob_locations_by_name(mob)
            
            # if we found a mob location and the list is not empty then get the path to that area id
            if mob_location is not None and len(mob_location) > 0:
                  # get the area id of the mob
                  area_id = mob_location[0]

                  # get the path to the area
                  path = self.mud_map.get_path(self.character.AREA_ID, area_id)

                  # if we found a path then return the path
                  if path is not None:
                        # append talk to the mob to the path
                        path.append("talk")
                        return path

      def talk_to_mob(self, mob, topic):
            # talk to the mob about the topic in our list
            first_mob_word = mob.split(" ", 2)[0]
            first_mob_word = first_mob_word.split("'", 2)[0] # cover for the apostrophe in the mob name
            talk_command = "ask {} {}".format(first_mob_word, topic)
            self.command_handler.process(talk_command)

      def decide_where_to_go(self):
            # for mob in self.target_mobs:
            if self.index >= len(self.target_mobs):
                  self.stop()
                  return []

            if not self.talking:
                  self.target_mob = self.target_mobs[self.index]
                  mob = Mob.get_mob_by_name(self.target_mob)

                  if mob is None:
                        magentaprint("Mob not found, skipping: {}".format(self.target_mob), False)
                        self.index += 1
                        return []

                  mobMessages = MobMessage.get_all_messages_by_mob(mob)

                  self.current_topics = []
                  for topic in self.talk_topics:
                        foundKeyword = False
                        for mobMessage in mobMessages:
                              if mobMessage.keyword == topic:
                                    foundKeyword = True
                                    break
                        if not foundKeyword:
                              self.current_topics.append(topic)

                  magentaprint("Found talking points: {} for {}".format(len(self.current_topics), self.target_mob), False)
                  if len(self.current_topics) == 0:
                        magentaprint("No talking points found, skipping: {}".format(self.target_mob), False)
                        self.index += 1
                        return []

                  magentaprint("Looking {} for mob: {}".format(self.index, self.target_mob), False)
                  # get the path to the mob
                  try:
                        path = self.get_path_to_target_mob(self.target_mob)
                  except:
                        magentaprint("Error getting path to mob, skipping: {}".format(self.target_mob), False)
                        # we can't path to this mob so skip it
                        self.index += 1
                        path = []

                  # if we found a path then return the path
                  if len(path) > 0:
                        self.talking = True
                        return path
            else:
                  magentaprint("Talking to mob: {}".format(self.target_mob), False)
                  # talk to the mob about all the topics in our list
                  for topic in self.current_topics:                        
                        self.talk_to_mob(self.target_mob, topic)
                        time.sleep(0.5)
                  self.talking = False
                  self.index += 1  
            
            return []
      
      # do go hooks for talking to a mob
      def do_go_hooks(self, exit_str):
            # if we are going to talk to a mob then set the talking flag to true
            if exit_str == "talk":
                  self.talking = True
                  time.sleep(1)
                  return True
            else:
                  return super().do_go_hooks(exit_str)