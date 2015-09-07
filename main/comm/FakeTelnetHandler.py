
import sys, time, re

from db.Database import *
from db.MudMap import *
from db.MudArea import *

class FakeSocketOutput(object):
    def __init__(self, text=""):
        self.text = text

    def decode(self, format="", errors=""):
        return self.text

class FakeTelnetSocket(object):
    def __init__(self, mud_map):
        self.content = ["[90 H 17 M]"]
        self.mud_map = mud_map
        self.whois_string = None

    def initialize_content(self, character_name):
        self.inventory_string = "You have: an awl, six small lamps, six small knives, a buckler, a burnt ochre potion, a hammer, a large bag, a large mace, two large sacks, a long sword, seven silver chalices, a silver torch, two small lamps, six steel bottles, five steel rings, two stilletos.\n"
        spaces = "                      "[0:22 - len(character_name)]
        
        self.whois_string = (
            "Player                Cls Gen [Lv]Title                      Age   Race      \n"
            "-----------------------------------------------------------------------------\n" + 
            character_name + spaces + "Mon  M  [12]Brother                    16    Human\n"
            # "Derp                  Mon  M  [12]Brother                    16    Human\n")
        )
        self.spells_string = (
            "\n\r"
            "/=== Combat Spells ======================================================\\\n\r"
            "| Level Earth        Wind         Fire         Water        Astral       |\n\r"
            "|   1   Rumble       Hurt                      Blister                   |\n\r"
            "|   2                Dustgust                                            |\n\r"
            "|   3                                                                    |\n\r"
            "|   4                                                                    |\n\r"
            "|   5                                                                    |\n\r"
            "/================== Healing and Protection ==============================\\\n\r"
            "|   Vigor            Mend-Wounds                                         |\n\r"
            "|                                     Protection                         |\n\r"
            "/======================================= Miscellaneous ==================\\\n\r"
            "|   Light                                                                |\n\r"
            "|   Show-Aura                                                            |\n\r"
            "/===================================================== Running Spells ===\\\n\r"
            "|                                   none                                 |\n\r"
            "\========================================================================/\n\r"

        )

        self.time_string = '                      Meditate   *READY*\n                         Touch   3:25 minutes remaining\n'
        self.equipment = (
            "You see " + character_name + " the Human Vicar.\n" \
            "He is in general good health.\n" \
            "On body:   some chain mail armour\n"   
            "On arms:   some chain mail sleeves\n"
            "On legs:   some chain mail leggings\n"
            "On neck:   a grey cloak\n"
            "On neck:   a traveller's cross\n"
            "On hands:  some chain mail gloves\n"
            "On head:   a chain mail hood\n"
            "On feet:   some chain mail boots\n"
            "On face:   some spectacles\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "On finger: an iron ring\n"
            "Shield:    a cast iron shield\n"
            "Wielded:   a morning star\n"
        )

        self.info_string = (
            "/============================== Overview ==================================\\\n\r"
            "|         " + character_name + " the Human, an Enlightened Brother of the 13th level      |\n\r"
            "|                  Your preferred alignment is dusty red                   |\n\r"
            "\==========================================================================/\n\r"
            "\n\r"
            " /==== Attributes =====\  /======= Weapons =====\  /======= Magic ========\\\n\r"
            " |       Str : 20      |  |     Sharp   : 0  %  |  |     Earth : 0  %     |\n\r"
            " |       Dex : 19      |  |     Thrust  : 0  %  |  |     Wind  : 0  %     |\n\r"
            " |       Con : 17      |  |     Blunt   : 87 %  |  |     Fire  : 45 %     |\n\r"
            " |       Int : 5       |  |     Pole    : 0  %  |  |     Water : 0  %     |\n\r"
            " |       Pty : 6       |  |     Missile : 0  %  |  |    Astral : 0  %     |\n\r"
            " \=====================/  \=====================/  \======================/\n\r"
            "\n\r"
            " /===== Status 1 ======\  /====== Status 2 =====\  /=====  Status 3 ======\\\n\r"
            " |   Curr HP : 86      |  |     Exp : 440607    |  | GameTime :  25:22:47 |\n\r"
            " |    Max HP : 89      |  |    Gold : 1578462   |  | Game Age : 16        |\n\r"
            " |   Curr MP : 1       |  |  -Needed to Level-  |  |                      |\n\r"
            " |    Max MP : 27      |  |     Exp : 560992    |  |   Weight : 113       |\n\r"
            " |        AC : 0       |  |    Gold : 70124     |  |  Objects : 33        |\n\r"
            " \=====================/  \=====================/  \======================/\n\r"
        )

        self.drop_string = (
            "You drop a %s.\n"
            "Thanks for recycling.\n"
            "You have 13612 gold.\n"
        )
        self.current_area = ""
        self.current_mud_area = None
        self.current_monster_list = []
        self.fso = FakeSocketOutput()

    def connect(host="", port=""):
        #connection string
        print ("Connected to FakeTelnetSocket!")

    def write(self, command):
        #re.match("bot ?$|bot [0-9]+$", user_input)
        #M_obj = re.search("[0-9]+", user_input)
        if not self.whois_string:
            # The first written string is the character's name for login
            self.initialize_content(command)
            self.write("genaid 336")
        elif command == "":
            self.content.append("[96 H 20 M] ")
        elif command == "i":
            self.content.append(self.inventory_string)
        elif re.match("whois (.+?)", command):
            self.content.append(self.whois_string)
        elif re.match("spells", command):
            self.content.append(self.spells_string)
        elif re.match("info", command):
            self.content.append(self.info_string)
        elif re.match("time", command):
            self.content.append(self.time_string)
        elif re.match("c show", command):
            self.content.append("You glow with a grey aura.\n")
        elif re.match("genaid [\d]*", command): #OUTPUT AN AREA
            M_obj = re.search("genaid ([\d]*)", command)
            area = Area.get_area_by_id(int(M_obj.group(1)))
            self.gen_area(area)
        elif command == "l":
            self.content.append(str(self.show_current_area()))
        elif command == "lself":
            self.content.append(str(self.equipment))
        elif re.match("addmob .+", command): #OUTPUT AN AREA
            M_obj = re.search("addmob (.+)", command)
            mob = str(M_obj.group(1))
            self.current_monster_list.append(mob)
            mob_arrived_string = "An " + mob + " just arrived.\n"
            self.content.append(mob_arrived_string)
        elif re.match("mobflee .+? .+", command):
            M_obj = re.search("mobflee (.+?) (.+)", command)
            mob = str(M_obj.group(1))
            direction = str(M_obj.group(2))
            flee_string = "The " + mob + " flees to the " + direction + ".\n"
            self.content.append(flee_string)
        elif re.match("mobdead .+", command):
            M_obj = re.search("mobdead (.+)", command)
            mob = str(M_obj.group(1))
            dead_string = "Your attack overwhelms the " + mob + " and he collapses!\nYour enemy, the " + mob + " has been defeated.\nYou gain 11 experience.\n"
            self.current_monster_list = []
            self.content.append(dead_string)
        elif re.match("go .+", command):
            M_obj = re.search("go (.+)", command)
            direction = str(M_obj.group(1))
            exit = ExitType(name=direction)
            mud_area = self.current_mud_area.get_area_to_from_exit(exit)
            self.gen_area(mud_area.area)
        elif re.match("break (.+)", command):
            M_obj = re.search("break (.+)", command)
            item = str(M_obj.group(1))
            break_string = "Your " + item + " fell apart.\n"
            self.content.append(break_string)
        elif re.match("drop (.+)", command):
            M_obj = re.search("drop (.+)", command)
            item = str(M_obj.group(1))
            drop_string = self.drop_string % item
            self.content.append(drop_string)
        elif re.match("sell (.+)", command):
            M_obj = re.search("sell (.+)", command)
            item = str(M_obj.group(1))
            sell_string = "The shopkeep gives you 30 gold for " + item + "."
            self.content.append(sell_string)
        elif re.match("echo (.+)", command):
            M_obj = re.search("echo (.+)", command)
            echo = str(M_obj.group(1))
            self.content.append(echo + "\n")
        elif re.match("quit", command) or re.match("quilt", command):
            self.content.append("Goodbye! Come back soon.")

    def gen_area(self, area):
        self.current_mud_area = MudArea(area)
        #(.+?\n\r)((?:\n\r.+)*)?(\n\rObvious exits: .+?[\n\r]?.+?\.)\n\r(You see .+?[\n\r]?.+?\.)?[\n\r]?(You see .+?[\n\r]?.+?\.)?
        area_string = (area.name + "\n\r\n\r" +
                      str(area.description) + "\n\r" +
                      "Obvious exits: ")
        i = 0
        while (i < (len(self.current_mud_area.area_exits) - 1)):
            area_string += str(self.current_mud_area.area_exits[i].exit_type.name) + ", "
            i += 1

        area_string += self.current_mud_area.area_exits[i].exit_type.name + "."

        self.current_area = area_string
        self.content.append(str(self.show_current_area()))

    def show_current_area(self):
        area_string = self.current_area

        if len(self.current_monster_list) is not 0:
            area_string += "\n\rYou see "

            i = 0
            while (i < (len(self.current_monster_list) - 1)):
                mob = str(self.current_monster_list[i])
                area_string += "a " + mob + ", "
                i += 1

            area_string += str(self.current_monster_list[i]) + "."

        return area_string + "\n\r"

    def read_some(self):
        if len(self.content) is not 0:
            fso = FakeSocketOutput(self.content.pop(0))
            return fso
        else:
            return FakeSocketOutput()

    def close(self):
        derp = False

    def get_socket(self):
        return 1

class FakeTelnetHandler(object):
    def __init__(self):
        self.mud_map = MudMap()
        self.tn = self.connect_to_MUD()
        self.tn.connect()

        self.echoing = True
        # self.tn.write("genaid 336") #lets start us in the chapel
        #self.tn.write("addmob spiv") #most everything will fight this

    def write(self, command):
        if self.echoing:
            magentaprint('{' + command + '}',False)

        self.tn.write(command)

    def connect_to_MUD(self):
        return FakeTelnetSocket(self.mud_map) 
        # No need to call open (http://www.python.org/doc/2.5.2/lib/module-telnetlib.html)

    def close(self):
        self.tn.close()

    def get_socket(self):
        return self.tn.get_socket()

    def read_some(self):
        return self.tn.read_some()  # read_eager() would miss characters



