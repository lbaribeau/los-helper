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
            mud_map=None, target=None):
            super().__init__(character, command_handler, mud_reader_handler, mud_map)

            # self.travel_bot = TravelBot(self.char, self.command_handler, mud_map)
            self.talking = False
            self.current_topics = []
            self.target_mobs = [
                  "Farside",
                  # "Dwar", # completed dialogue
                  # "Mayor Demlin", # completed dialogue
                  # "Commander Rilmenson", # completed dialogue
                  # "General", # completed dialoguestop
                  # "Madame Zara", # completed dialogue
                  # "Ringmaster", # doesn't respond to anything
                  # "Farmer Grangers Ghost", # completed dialogue
                  # "Farmer Malbon", # completed dialogue
                  "Priestly Ghost",
                  # "Farmer Calmor", # completed dialogue
                  # "Farmer McDermott", # completed dialogue
                  # # "Druid Tutor", #buggy
                  # "Bertram Dalrum",  # doesn't respond to anything
                  # "Dame Brethil",  # doesn't respond to anything
                  # "Earl Mardley",  # doesn't respond to anything
                  # "Alaran the Market Manager",  # doesn't respond to anything
                  # "Douvan", "Queen Dalla", # completed dialogue
                  # "Jerrek", # completed dialogue
                  # "Tag", "Rag", # completed dialogue
                  # "Thomas Ironheart", # completed dialogue
                  # "Olarma", # completed dialogue
                  # "Master of Ceremonies",  # completed dialogue
                  # "Boris Ironfounder", # completed dialogue
                  # "Tendrurn", # completed dialogue
                  # "Brotain", # completed dialogue
                  # "Rimark", # completed dialogue
                  # "Aldo", # completed dialogue
                  # "Horbuk", # completed dialogue
                  # "Gerdevarashimora",
                  # "Volman the Inhumer",
                  # "The Master Artificer",
                  # "Kin'Tal", # completed dialogue
                  # "The Archbishop", # trainer
                  # "Tardan", # completed dialogue
                  # "Trantas", #hardcore arena NPC
                  # "Gregor", # completed dialogue
                  # "Farmer Viladin", # completed dialogue
                  # "Cal the Hermit", # completed dialogue
                  # "Farmer Woldis", # completed dialogue
                  # "Rancher Renstone", # completed dialogue
                  # "Rancher Plover", # completed dialogue
                  # "Annette Plover", # completed dialogue
                  # "White Mage", # trainer
                  # "The Barding Lord", # trainer
                  # "Knight Errant", # trainer
                  "barbarian shaman",
                  "Corien",
                  # "Lyron the Elder","Shaldena the Red","Garbo the Hobbit","Whiteblade the Barbarian", # completed dialogue
                  # "Great Druid",
                  # "Teamleader Egan", # doesn't respond to anything
                  # "Trent the Merchant", # doesn't respond to anything
                  # "Grand Master Yang-Shi", # completed dialogue
                  # # "Sensei", # trainer
                  # "Dojo Administrator", # completed dialogue
                  # "Dr'Tel's Ghost", # completed dialogue
                  # "Al'Sik the Carver", # completed dialogue
                  # "Zi'Cab the Chieftan", # doesn't respond to anything
                  # "Vas'Polu the HawkMaster","Byr'Ula the Smith","Ha'Chans the Shaman", # completed dialogue
                  # "Th'kit the HorseMaster", # completed dialogue
                  # "Druid Galm", # completed dialogue
                  # "Forest Master",
                  "Broad Leaf",
                  "Red Crown",
                  "Lord Tamaran",
                  # "Tario", # completed dialogue
                  # "Lady Denlise",  # completed dialogue 
                  # "Vickie", # completed dialogue
                  # "Matriarch Sara",
                  # "Lady Arielle",
                  "Lord Arduis",
                  "Lady Jenlira", # completed dialogue
                  # "Bhezkam",
                  "Ironbark", # not found but mentioned by Jenlira!!!
                  # "Esrhae", # completed dialoguel
                  # "Haelyn", # doesn't respond to anything
                  # "Caethrodyn", # doesn't respond to anything
                  # "Robar Greybeard", # completed dialogue
                  "Greenbough the Dryad",
                  "Deep Root", # completed dialogue
                  "Oakheart",
                  "Winter's Watcher", # completed dialogue
                  # "Agguedian's Simulcrum", # not pathable
                  # "rough-hewn golem", # completed dialogue
                  # "Cheryn", # completed dialogue
                  # "Maco Bail", # Behind locked door
                  "Manic Soothsayer",
                  # "Elder Barthrodue", # completed dialogue
                  # "Goourd", # completed dialogue
                  # "Old Man James", # completed dialogue
                  # 'Haram', # completed dialogue
                  # "GuildMaster Cuvelas", # trainer
                  # "Chiaru Maradiu",
                  # "Thereze", # completed dialogue
                  # "Qimoth", # completed dialogue
                  # "Joffi the Mystic", # completed dialogue
                  # "Gorban", # completed dialogue
                  # "Pansy", # completed dialogue
                  # "Kelluran", # completed dialogue
                  # "Ordaran the White", # completed dialogue
                  # "Corellan", # completed dialogue
                  # "Picharos Silvermane", # completed dialogue
            ]

            if target is not None:
                  self.target_mobs = [target]

            self.index = 0

            self.talk_topics = [
                  "", # empty string to talk to the mob
                  "hello",
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
                  "mix",
                  "brew",
                  "forget",
                  "remember",
                  "memory",
                  "conquer",
                  "bloodlust",
                  # leveling
                  # "train",
                  # "level",
                  # "one",
                  # "two",
                  # "three",
                  # "four",
                  # "five",
                  # "six",
                  # "seven",
                  # "eight",
                  # "nine",
                  # "ten",
                  # "eleven",
                  # "twelve",
                  # "thirteen",
                  # "fourteen",
                  # "fifteen",
                  # "sixteen",
                  # "seventeen",
                  # "eighteen",
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
                  "dracae",
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
                  "frog",
                  "spawning",
                  "sprite",
                  "aqueous",
                  "scarecrow",
                  "skeletal",
                  "lich",
                  "spirit",
                  "spectre",
                  "ooze",
                  # things
                  "secret",
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
                  "golden",
                  "silver",
                  "copper",
                  "iron",
                  "steel",
                  "weapon",
                  "magic",
                  "magical",
                  "spell",
                  "armor",
                  "armour",
                  "gauntlet",
                  "claw",
                  "treasure",
                  "chest",
                  "gem",
                  "fire",
                  "water",
                  "mnemosyne",
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
                  "broken",
                  "sword",
                  "handle",
                  "hilt",
                  "blade",
                  "blades",
                  "axe",
                  "staff",
                  "dagger",
                  "hammer",
                  "mace",
                  "bow",
                  "heartseeker", # magic bow at the green mound
                  "spear",
                  "arrow",
                  "whip",
                  "chain",
                  "instrument",
                  "venom",
                  "juices",
                  "arrow",
                  "eye",
                  "amulet",
                  "medallion",
                  "ring",
                  "snuff",
                  "mushroom",
                  "fungal",
                  "fungus",
                  "king",
                  "statue",
                  "moth",
                  "jade",
                  "raw",
                  "nugget",
                  "immadhun",
                  "block",
                  "stone",
                  "ascoula", # stone that Jerrek is looking for
                  "anvil",
                  "crystal",
                  "hide",
                  "skin",
                  "carpet",
                  "tear",
                  "teardrop",
                  "body",
                  "strange",
                  "mechanism",
                  "machine",
                  "heart",
                  "cerulindial",
                  "hitlist",
                  "master",
                  "remedy",
                  "lime",
                  # spells
                  "blind",
                  "clairvoyance",
                  "invisibility",
                  "levitate",
                  "float",
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
                  "breathe-water",
                  "breathe",
                  "stun",
                  "bind",
                  "confusion",
                  "enchant",
                  # places
                  "cloud",
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
                  "rock",
                  "ranch",
                  "monolith",
                  "shrine",
                  "divide",
                  "great",
                  "blasted",
                  "plains",
                  "fens",
                  "desert",
                  "grove",
                  "echuske",
                  "green",
                  "red",
                  "blue",
                  "yellow",
                  "mound",
                  "lake",
                  "fleet",
                  "village",
                  "tertinantageal",
                  "gallenduraleal",
                  "citadel",
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
                  "morag",
                  "flame",
                  "night",
                  "gem",
                  "granite",
                  "warder",
                  "mora",
                  "chao",
                  "tipshy",
                  "flametongue",
                  "thad",
                  "thadden",
                  "destroyer",
                  "arrum",
                  "giantstone",
                  "hrootim",
                  "starfire",
                  "blackstar",
                  "sage",
                  "eilya", # dark knight
                  "mort", # dark knight
                  "vaun", # dark knight
                  "kervack", # dark knight
                  "aldoram", # paladin turned dark knight
                  # "jagg", # greatest fighter in all the land
                  "daray", # "She is powerful and knows many secrets,many dark things. I consider that special
                  "fisherman",
                  "helyana",
                  "dalough",
                  "antitheus",
                  "elnor",
                  "garin", # blade who never stood by
                  "grindig",
                  "bloody",
                  "grumdug",
                  "elder",
                  "bludnug",
                  "snarus",
                  "winter",
                  "watcher",
                  "galdor",
                  "ironhammer",
                  # "jagg", #players the criers speak about
                  # "crow", #players the criers speak about
                  # "stahn", #players the criers speak about
                  # "bruno", #players the criers speak about
                  # "valiant", #players the criers speak about
            ]

            # brute_forced_responses  = MobMessage.get_messages_with_responses()
            # self.talk_topics = self.get_unique_keywords(brute_forced_responses)

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
            if self.stopping:
                  self.stop()
                  return []
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

                  self.smart_get_topics(mobMessages)

                  magentaprint("Found talking points: {} for {}".format(len(self.current_topics), self.target_mob), False)
                  magentaprint("Topics: {}".format(self.current_topics), False)
                  if len(self.current_topics) == 0:
                        magentaprint("No talking points found, skipping: {}".format(self.target_mob), False)
                        self.index += 1
                        return []

                  foundMob = False
                  for mob in [str(m) for m in self.character.mobs.list]:
                        if self.target_mob == mob:
                              foundMob = True
                              break
                  
                  if foundMob:
                        self.talking = True
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
                  # is the mob in the area?
                  foundMob = False

                  for mob in [str(m) for m in self.character.mobs.list]:
                        if self.target_mob == mob:
                              foundMob = True
                              break
                  if foundMob:
                        magentaprint("Talking to mob: {}".format(self.target_mob), False)
                        # talk to the mob about all the topics in our list
                        while len(self.current_topics) > 0:
                              if self.stopping:
                                    self.stop()
                                    return []
                              for topic in self.current_topics:                        
                                    self.talk_to_mob(self.target_mob, topic)
                                    time.sleep(0.5)
                              mob = Mob.get_mob_by_name(self.target_mob)
                              mobMessages = MobMessage.get_all_messages_by_mob(mob)
                              self.smart_get_topics(mobMessages, use_area=True)
                        self.talking = False
                        self.index += 1
                  else:
                        self.talking = False
                        self.index += 1
                        magentaprint("Mob not found, skipping: {}".format(self.target_mob), False)
            
            return []

      def get_topics(self, mobMessages):
            self.current_topics = []
            for topic in self.talk_topics:
                  foundKeyword = False
                  for mobMessage in mobMessages:
                        if mobMessage.keyword.lower() == topic.lower():
                              foundKeyword = True
                              break
                  if not foundKeyword:
                        self.current_topics.append(topic)

      def get_topics_from_string(self, content, strip_s=False):
            messages = re.sub(r'[!\.\?,\'\"]',' ',content)

            temp_topics = []
            for word in messages.split(' '):
                  if len(word) > 3 and word not in temp_topics:
                        if strip_s:
                              word = re.sub(r's$','',word)
                        temp_topics.append(word.lower())
            return temp_topics

      def smart_get_topics(self, mobMessages, use_area=False):
            messages = ""
            self.current_topics = []
            for mobMessage in mobMessages:
                  if mobMessage.message is not None:
                        messages += " " + mobMessage.message
            
            # join together all the mob names into a string list and lowercase it all
            mob_names = ' '.join(self.target_mobs).lower()
            messages += " " + mob_names

            # regex replace all punctuation in messages with spaces
            # for each word greater than 3 letters in the messages list
            # if the word is not in the current topics or mobMessage keywords then add it to current topcis
            temp_topics = self.get_topics_from_string(messages)
            
            for talk_topic in self.talk_topics:
                  if talk_topic.lower() not in temp_topics:
                        temp_topics.append(talk_topic.lower())

            if use_area:
                  area = self.character.MUD_AREA.area
                  area_topics = self.get_topics_from_string(area.description)

                  for area_topic in area_topics:
                        if area_topic.lower() not in temp_topics:
                              temp_topics.append(area_topic.lower())

            for temp_topic in temp_topics:
                  foundKeyword = False
                  for mobMessage in mobMessages:
                        if mobMessage.keyword.lower() == temp_topic.lower():
                              foundKeyword = True
                              break
                  if not foundKeyword:
                        self.current_topics.append(temp_topic.lower())

      def get_unique_keywords(self, mobMessages):
            keywords = []
            for mobMessage in mobMessages:
                  topic = mobMessage.keyword.lower()
                  if topic not in keywords:
                        keywords.append(topic)
            return keywords

      # do go hooks for talking to a mob
      def do_go_hooks(self, exit_str):
            # if we are going to talk to a mob then set the talking flag to true
            if exit_str == "talk":
                  self.talking = True
                  time.sleep(1)
                  return True
            else:
                  return super().do_go_hooks(exit_str)