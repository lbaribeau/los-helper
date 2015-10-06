
import sys, time, re
import random

from db.Database import *
from db.MudMap import *
from db.MudArea import *
from command.Go import Go

class FakeSocketOutput(object):
    def __init__(self, text=""):
        self.text = text

    def decode(self, format="", errors=""):
        return self.text

class FakeTelnetSocket(object):
    def __init__(self, mud_map):
        self.content = ["[86 H 1 M]: "]
        self.mud_map = mud_map
        self.whois_string = None

    def initialize_content(self, character_name):
        self.current_area = ""
        self.current_mud_area = None
        self.current_monster_list = ['spiv', 'housewife', 'sawmill operator', 'militia soldier', 'sword swallower']
        self.fso = FakeSocketOutput()
        self.rng = 0
        self.hp = 86
        self.pots = ['small restorative'] * 2 + ['small flask'] * 2 + ['white potion'] * 2
        self.flask_rng = 0

        self.inventory_string = "You have: an awl, six small lamps, six small knives, a buckler, a burnt ochre potion, \n\r" \
            "a hammer, a large bag, a large mace, two large sacks, a long sword, seven silver chalices, a silver torch, \n\r" \
            "two small flasks, two small lamps, two small restoratives, six steel bottles, five steel rings, two stilletos, \n\r" \
            "two white potions.\n"
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

    def connect(host="", port=""):
        #connection string
        print ("Connected to FakeTelnetSocket!")

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
        # Assumes is

    def write(self, command):
        #re.match("bot ?$|bot [0-9]+$", user_input)
        #M_obj = re.search("[0-9]+", user_input)
        if not self.whois_string:
            # The first written string is the character's name for login
            self.initialize_content(command)
            self.write('genaid 2')
            # self.write('addmob spiv')

        if command == '':
            self.content.append('[' + str(self.hp) + ' H 27 M]: ')
        elif re.match('whois (.+?)', command):
            self.content.append(self.whois_string)
        elif re.match('spells', command):
            self.content.append(self.spells_string)
        elif re.match('info?', command):
            self.content.append(self.info_string)
        elif re.match('time', command):
            self.content.append(self.time_string)
        elif re.match('c show', command):
            self.content.append('You glow with a grey aura.\n')
        elif re.match('genaid [\d]+', command): #OUTPUT AN AREA
            M_obj = re.search('genaid ([\d]*)', command)
            area = Area.get_area_by_id(int(M_obj.group(1)))
            self.gen_area(area)
        elif command == 'l':
            self.content.append(str(self.show_current_area()))
        elif command == 'lself' or command == 'eq':
            self.content.append(str(self.equipment))
        elif command.startswith('addmob '):
            self.addmob(command[7:])
        elif re.match('mobflee .+? .+', command):
            M_obj = re.search('mobflee (.+?) (.+)', command)
            self.mobflee(M_obj.group(1), M_obj.group(2))
        elif command.startswith('mobdead '):
            self.mobdead(command[8:])
        elif command == 'me':
            self.content.append('You feel at one with the universe.')
        elif re.match(r"(tou?|touc?|touch) [A-Za-z' ]+", command):
            m = re.match(r"(tou?|touc?|touch) (?P<mob>[A-Za-z' ]+)", command)
            self.content.append('You touched the ' + m.group('mob') + ' for 102 damage.\n\r')
        elif command == 'rest':
            self.hp = 89
            self.content.append('[89 H 27 M]: You feel the benefits of resting.\n\r')
        elif command.startswith('k '):
            # self.kill(command[2:])
            self.mob_combat(command[2:])
        elif re.match(r'(ca?|cast?) [a-z]+ .+?', command):
            m = re.match(r"(ca?|cast?) (?P<spell>[a-z]+) (?P<mob>[A-Za-z0-9']+)", command)
            # self.cast(m.group('spell'), m.group('mob'))
            self.mob_combat(m.group('mob'), m.group('spell'))
        elif command.startswith('go ') and len(command) > 3:
            self.gen_next_area(command[2:])
        elif Go.is_direction(command):
            self.gen_next_area(expand_direction(command))
        elif command == 'i':
            self.content.append(self.inventory_string)
        elif re.match('break (.+)', command):
            M_obj = re.search('break (.+)', command)
            item = str(M_obj.group(1))
            break_string = 'Your ' + item + ' fell apart.\n'
            self.content.append(break_string)
        elif re.match('drop (.+)', command):
            M_obj = re.search('drop (.+)', command)
            item = str(M_obj.group(1))
            drop_string = self.drop_string % item
            self.content.append(drop_string)
        elif re.match('sell (.+)', command):
            M_obj = re.search('sell (.+)', command)
            item = str(M_obj.group(1))
            sell_string = 'The shopkeep gives you 30 gold for ' + item + '.'
            self.content.append(sell_string)
        elif command == 'use restorative':
            if 'small restorative' in self.pots:
                self.pots.remove('small restorative')
                self.hp = self.hp + 1
                self.content.append('Potion drank.\n\rYou feel much better.\n\rA small restorative disintegrates.\n\r')
                self.content.append('[ ' + str(self.hp) + ' H 27 M]: ')
        elif command == 'use flask':
            if 'small flask' in self.pots:
                self.flask_rng = self.flask_rng + 1 % 2
                self.hp = self.hp + 2
                if self.flask_rng == 1:
                    self.content.append('Potion drank.\n\rYou feel much better.\n\r')
                else:
                    self.pots.remove('small flask')
                    self.content.append('Potion drank.\n\rYou feel much better.\n\rA small flask disintegrates.\n\r')
                self.content.append('[ ' + str(self.hp) + ' H 27 M]: ')
        elif re.match('echo (.+)', command):
            M_obj = re.search('echo (.+)', command)
            echo = str(M_obj.group(1))
            self.content.append(echo + '\n')
        elif re.match('quit', command) or re.match('quilt', command):
            self.content.append('Goodbye! Come back soon.')

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

    def gen_next_area(self, direction):
        exit = ExitType(name=direction)
        mud_area = self.current_mud_area.get_area_to_from_exit(exit)

        if mud_area is None:
            self.content.append("You can't go that way.\n\r")
        else:
            self.gen_area(mud_area.area)

    def show_current_area(self):
        area_string = self.current_area
        n_monsters = len(self.current_monster_list)

        if n_monsters != 0:
            area_string += "\n\rYou see "
            # i = 0
            # while i < len(self.current_monster_list) - 2:
                # mob = str(self.current_monster_list[i])
                # area_string += "a " + mob + ", "
                # i += 1
            # area_string += str(self.current_monster_list[i]) + "."
            for m in self.current_monster_list[0:n_monsters-1]:
                area_string += 'a ' + m + ', '

            area_string += 'a ' + self.current_monster_list[n_monsters-1] + '.' 

        return area_string + "\n\r"

    def addmob(self, mob):
        self.current_monster_list.append(mob)
        mob_arrived_string = 'An ' + mob + ' just arrived.\n'
        self.content.append(mob_arrived_string)

    def mobflee(self, mob, direction):
        flee_string = 'The ' + mob + ' flees to the ' + direction + '.\n'
        self.mob_lost_battle(mob, flee_string)

    def mobdead(self, mob):
        dead_string = 'Your attack overwhelms the ' + mob + ' and he collapses!\nYour enemy, the ' + mob + ' has been defeated.\nYou gain 11 experience.\n'
        self.mob_lost_battle(mob, dead_string)
    
    def mob_lost_battle(self, mob, lost_string):
        if mob in self.current_monster_list:
            self.current_monster_list.remove(mob)
        # else:
        #     self.current_monster_list = []
        self.content.append(lost_string)

    def mob_combat(self, mob, spell=None):
        # if mob in self.current_monster_list:
        sorted_mob_list = sorted(self.current_monster_list)
        startswith_boolean_list = [m.startswith(mob) for m in sorted_mob_list]
        if any(startswith_boolean_list):
            # mob = self.current_monster_list.index(startswith_boolean_list)
            # mob = self.current_monster_list[startswith_boolean_list.index(1)]
            mob = sorted_mob_list[startswith_boolean_list.index(1)]
            if spell:
                self.content.append('You cast a ' + spell + ' spell on the ' + mob + ' for 12 damage.\n\r')
            else:
                self.content.append('You lash out and thump the ' + mob + ' for 8 damage.\n\r')

            # r = random.randint(1,4)
            # if r == 1 or r == 2:
            #     return
            # else:
            #     self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
            # # elif r == 3:
            # #     self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
            # # else:
            # #     self.mobdead(mob)
            # self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
            if mob == 'sawmill operator':
                self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
            elif mob == 'housewife':
                if len(self.current_mud_area.area_exits) > 1:
                    self.mobflee(mob, str(self.current_mud_area.area_exits[1].exit_type.name))
                else:
                    self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
            elif mob == 'militia soldier':
                self.rng = (self.rng + 1) % 2
                self.hp = self.hp - 60
                if self.rng == 1 and self.hp > 60:
                    self.content.append('[' + str(self.hp) + ' H 27 M]: The militia soldier painfully head-butts you for 60 damage.')
                else:
                    self.mobdead(mob)
            elif mob == 'sword swallower':
                self.rng = (self.rng + 1) % 3
                self.hp = max(self.hp - 60, 0)
                self.content.append('[' + str(self.hp) + ' H 27 M]: The sword swallower painfully head-butts you for 60 damage.')
                if self.hp == 0:
                    self.hp = 1
                    self.content.append("You are overwhelmed by the sword swallower's attack and you collapse!")
                self.content.append('[1 H 27 M]: ')
            else:
                self.rng = (self.rng + 1) % 3
                if self.rng == 0:
                    self.mobdead(mob)
            # self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
        else:
            if spell:
                self.content.append('They are not here.\n\r')
            else:
                self.content.append('Attack what?\n\r')

    def kill(self, mob):
        self.mob_combat(mob, 'You lash out and thump the ' + mob + ' for 8 damage.\n\r', 'Attack what?\n\r')

    def cast(self, spell, mob):
        self.mob_combat(mob, 'You cast a ' + spell + ' spell on the ' + mob + ' for 12 damage.\n\r', 'They are not here.\n\r')

class FakeTelnetHandler(object):
    def __init__(self):
        self.mud_map = MudMap()
        self.tn = self.connect_to_MUD()
        self.tn.connect()

        self.echoing = True

    def write(self, command):
        if self.echoing:
            magentaprint('{' + command + '}',False)

        self.tn.write(command)

    def connect_to_MUD(self):
        return FakeTelnetSocket(self.mud_map) 

    def close(self):
        self.tn.close()

    def get_socket(self):
        return self.tn.get_socket()

    def read_some(self):
        return self.tn.read_some()

def expand_direction(d):
    if d == 'se':
        return 'southeast'
    elif d == 'sw':
        return 'southwest'
    elif d == 'ne':
        return 'northeast'
    elif d == 'nw':
        return 'northwest'
    elif d == 's': 
        return 'south'
    elif d == 'w':
        return 'west'
    elif d == 'e':
        return 'east'
    elif d == 'n':
        return 'north'
    elif re.match('do?|down?', d):
        return 'down'
    elif re.match('up?$', d):
        return 'up'
    elif re.match('out?$', d):
        return 'out'
    else:
        magentaprint('Go.expand_direction() error case.')
        return ''

