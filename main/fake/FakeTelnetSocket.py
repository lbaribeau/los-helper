
import re

from db.MudArea import *
from fake.FakeSocketOutput import FakeSocketOutput
from fake.FakeInventory import FakeInventory
from fake.FakeEquipment import FakeEquipment
from command.Go import Go
from fake.FakeBuy import FakeBuy
from fake.fake_use import FakeUse
from fake.fake_mobs.fake_mobs import Actor
from fake.fake_character import FakeCharacter

class FakeTelnetSocket(object):
    def __init__(self, mud_map):
        self.char = FakeCharacter()
        self.socket_output = ["[%s H %s M]: " % (self.char.hp, self.char.mp)]
        self.mud_map = mud_map
        self.whois_string = None
        self.actor = Actor(self.char, self.socket_output)

    def initialize_socket_output(self, character_name):
        self.char.name = character_name
        self.current_area = ""
        self.current_mud_area = None
        self.current_monster_list = [
            'acrobat', 'juggler',                                 # chasing
            'kobold champion', # weapon shatter
            # 'kobold sentry', # spear break
            'large kobold',    # maul hammer break
            # 'militia soldier',                                    # potting
            'tabby cat', 
            self.actor.name,
        ]
        self.fso = FakeSocketOutput()
        self.rng = 0
        self.pots = ['small restorative'] * 2 + ['small flask'] * 2 + ['white potion'] * 2
        self.flask_rng = 0
        self.weapon = ''
        # self.inventory_string = "You have: an awl, six small lamps, six small knives, a buckler, a burnt ochre potion, \n\r" \
        #     "a hammer, a large bag, a large mace, two large sacks, a long sword, seven silver chalices, a silver torch, \n\r" \
        #     "two small flasks, two small lamps, two small restoratives, six steel bottles, five steel rings, two stilletos, \n\r" \
        #     "two white potions.\n"
        self.inventory = FakeInventory(['awl'] + ['small lamp'] * 6 + ['small knive'] * 6 + ['large sack'] * 2 + \
            ['silver chalice'] * 7 + ['small flask'] * 2 + ['small lamp'] * 2 + ['small restorative'] * 2 + \
            ['steel bottle'] * 6 + ['steel ring'] * 6 + ['stilleto'] * 2 + ['white potion'] * 2 + ['maul hammer'] * 3 + \
            ['buckler', 'burnt ochre potion', 'hammer', 'large bag', 'large mace', 'long sword', 'silver torch', \
             'spectacles', 'title deeds', 'morning star'])
        self.inventory.set_unusable('morning')
        self.inventory.set_unusable('maul 2')
        self.inventory.set_unusable('maul 3')
        self.inventory.set_unusable('ring 3') 
        self.inventory.set_unusable('ring 5')
        self.char.inv = self.inventory
        # self.inventory = FakeInventory({'awl':1, 'small lamp':6, 'small knife':6, 'large sack':2, 'silver chalice':6, 'small flask':2, \
        #     'small lamp':2, 'small restorative':2, 'steel bottle':6, 'steel ring':6, 'stilleto':2, 'white potion':2, \
        #     'buckler':1, 'burnt ochre potion':1, 'hammer':1, 'large bag':1, 'large mace':1, 'long sword':1, 'silver torch':1, \
        #     'spectacles': 1, 'title deeds': 1, 'morning star': 1, 'maul hammer': 2
        # })
        self.char.equipment = FakeEquipment(self.char.name)
        self.buy = FakeBuy(self.inventory, self.socket_output)
        self.use = FakeUse(self.char, self.socket_output)

        spaces = "                      "[0:22 - len(self.char.name)]
        
        self.whois_string = (
            "Player                Cls Gen [Lv]Title                      Age   Race      \n"
            "-----------------------------------------------------------------------------\n" + 
            # "Derp                  Mon  M  [12]Brother                    16    Human\n")
            # self.char.name + spaces + "Mon  M  [12]Brother                    16    Human\n"
            self.char.name + spaces + "Mag  M  [08]Keeper                    16    Human\n"
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

        self.time_string = '                      Meditate   *READY*\n                         Touch   3:25 minutes remaining\n\r'

        self.info_string = (
            "/============================== Overview ==================================\\\n\r"
            "|         " + self.char.name + " the Human, an Enlightened Brother of the 13th level      |\n\r"
            "|                  Your preferred alignment is dusty red                   |\n\r"
            "\==========================================================================/\n\r"
            "\n\r"
            " /==== Attributes =====\  /======= Weapons =====\  /======= Magic ========\\\n\r"
            " |       Str : 20      |  |     Sharp   : 0  %  |  |     Earth : 0  %     |\n\r"
            " |       Dex : 19      |  |     Thrust  : 0  %  |  |     Wind  : 0  %     |\n\r"
            " |       Con : 17      |  |     Blunt   : 61 %  |  |     Fire  : 45 %     |\n\r"
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
        if len(self.socket_output) is not 0:
            fso = FakeSocketOutput(self.socket_output.pop(0))
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
            self.initialize_socket_output(command)
            self.write('genaid 2')
            # self.write('addmob spiv')
        if command == '':
            self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))
        elif re.match('whois (.+?)', command):
            self.socket_output.append(self.whois_string)
        elif re.match('spells', command):
            self.socket_output.append(self.spells_string)
        elif re.match('info?', command):
            self.socket_output.append(self.info_string)
        elif re.match('time', command):
            self.socket_output.append(self.time_string)
        elif re.match('c show', command):
            self.socket_output.append('You glow with a grey aura.\n\r')
        elif re.match('c (vi?|vigo?|vigor)', command):
            self.char.hp = min(self.char.maxhp, self.char.hp + 15)
            self.socket_output.append('Vigor spell cast.\n\r')
            self.socket_output.append('[%s H %s M]: ' % (str(self.char.hp), str(self.char.mp)))
        elif re.match('genaid [\d]+', command): #OUTPUT AN AREA
            M_obj = re.search('genaid ([\d]*)', command)
            area = Area.get_area_by_id(int(M_obj.group(1)))
            self.gen_area(area)
        elif command == 'l':
            self.socket_output.append(str(self.show_current_area()))
        elif command == 'lself':
            self.socket_output.append(self.char.equipment.lself())
        elif command == 'eq':
            magentaprint(self.char.equipment.output_string())
            self.socket_output.append(self.char.equipment.output_string())
        elif command.startswith('addmob '):
            self.addmob(command[7:])
        elif re.match('mobflee .+? .+', command):
            M_obj = re.search('mobflee (.+?) (.+)', command)
            self.mobflee(M_obj.group(1), M_obj.group(2))
        elif command.startswith('mobdead '):
            self.mobdead(command[8:])
        elif command == 'me':
            self.socket_output.append('You feel at one with the universe.\n\r')
        elif re.match(r"(tou?|touc?|touch) [A-Za-z' ]+", command):
            m = re.match(r"(tou?|touc?|touch) (?P<mob>[A-Za-z']+)", command)
            if self.get_mob_name(m.group('mob')):
                self.socket_output.append('You touched the ' + self.get_mob_name(m.group('mob')) + ' for 102 damage.\n\r')
            else:
                self.socket_output.append('Touch whom?')
        elif command.startswith('has'):
            self.socket_output.append('You feel yourself moving faster.\n\r')
        elif command == 'rest':
            self.char.hp = self.char.maxhp
            self.char.mp = self.char.maxmp
            self.socket_output.append('[%s H %s M]: You feel the benefits of resting.\n\r' % (self.char.hp, self.char.mp))
        elif command.startswith('k '):
            # self.kill(command[2:])
            self.mob_combat(command[2:])
        elif re.match(r'(ca?|cast?) [a-z]+ .+?', command):
            m = re.match(r"(ca?|cast?) (?P<spell>[a-z]+) (?P<mob>[A-Za-z0-9']+)", command)
            # self.cast(m.group('spell'), m.group('mob'))
            self.mob_combat(m.group('mob'), m.group('spell'))
        elif command.startswith('go ') and len(command) > 3:
            self.gen_next_area(command[3:])
        elif Go.is_direction(command):
            self.gen_next_area(expand_direction(command))
        elif command == 'i':
            self.socket_output.append(self.inventory.output_string())
        elif command.startswith('wie') and len(command.split(' ')) > 1:
            if self.char.equipment.weapon:
                self.socket_output.append("You're already wielding something.\n\r")
            else:
                w = self.inventory.get(command.partition(' ')[2])
                if w:
                    if w.unusable:
                        self.socket_output.append("You can't. It's broken.\n\r")
                    else:
                        self.socket_output.append("You wield a " + w.name + ".\n\r")
                        self.inventory.remove(command.split(' ')[1])
                        self.char.equipment.wield(w.name)
                else:
                    self.socket_output.append("You don't have that.\n\r")
        elif command.startswith('seco') and len(command.split(' ')) > 1:
            self.socket_output.append('You wield a spear in your off hand.\n\r')
            self.inventory.remove('spear')
            self.char.equipment.second('spear')
        elif re.match('break (.+)', command):
            M_obj = re.search('break (.+)', command)
            item = str(M_obj.group(1))
            break_string = 'Your ' + item + ' fell apart.\n\r'
            self.socket_output.append(break_string)
            self.char.inv.add(command.partition(' ')[2])
        elif re.match('drop (.+)', command):
            i = self.inventory.index(command.partition(' ')[2])
            if i > -1:
                self.socket_output.append(self.drop_string % self.inventory.l[i].name)
                self.buy.cant_carry = False
                self.inventory.remove(command.partition(' ')[2])
            else:
                self.socket_output.append("You don't have that.\n\r")
        elif re.match('sell (.+)', command):
            i = self.inventory.index(command.partition(' ')[2])
            if i > -1:
                self.socket_output.append('The shopkeep gives you 30 gold for a ' + self.inventory.l[i].name + '.\n\r')
                self.buy.cant_carry = False
                self.inventory.remove(command.partition(' ')[2])
            else:
                self.socket_output.append("You don't have that\n\r.")
        elif command.startswith('use '):
            self.use.do(command.partition(' ')[2])
        elif command.startswith('buy '):
            self.buy.do(command.partition(' ')[2])
        elif command == 'get all':
            self.socket_output.append("There's nothing here.\n\r")
        elif command.startswith('get '):
            self.socket_output.append("You get a %s." % command.partition(' ')[2])
            self.char.inv.add(command.partition(' ')[2])
        elif re.match('echo (.+)', command):
            M_obj = re.search('echo (.+)', command)
            echo = str(M_obj.group(1))
            self.socket_output.append(echo + '\n\r')
        elif re.match('quit', command) or re.match('quilt', command):
            self.socket_output.append('Goodbye! Come back soon.\n\r')

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
        self.socket_output.append(str(self.show_current_area()))  # one more newline?

    def gen_next_area(self, direction):
        exit = ExitType(name=self.get_whole_exit_name(direction))
        mud_area = self.current_mud_area.get_area_to_from_exit(exit)
        # magentaprint('gen_next_area() ' + direction + ', ' + str(exit) + '. mud_area:' + str(mud_area))

        if mud_area is None:
            self.socket_output.append("You can't go that way.\n\r")
        else:
            self.gen_area(mud_area.area)

    def get_whole_exit_name(self, first_letters):
        return self.get_full_name_of_target(first_letters, sorted([e.exit_type.name for e in self.current_mud_area.area_exits]))

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
        mob_arrived_string = 'An ' + mob + ' just arrived.\n\r'
        self.socket_output.append(mob_arrived_string)

    def mobflee(self, mob, direction):
        flee_string = 'The ' + mob + ' flees to the ' + direction + '.\n\r'
        self.mob_lost_battle(mob, flee_string)

    def mobdead(self, mob):
        dead_string = 'Your attack overwhelms the ' + mob + ' and he collapses!\nYour enemy, the ' + mob + ' has been defeated.\nYou gain 11 experience.\n\r'
        self.mob_lost_battle(mob, dead_string)
    
    def mob_lost_battle(self, mob, lost_string):
        self.rng = 0
        if mob in self.current_monster_list:
            self.current_monster_list.remove(mob)
        # else:
        #     self.current_monster_list = []
        self.socket_output.append(lost_string)

    def mob_combat(self, mob, spell=None):
        mob = self.get_mob_name(mob)
        if mob:
            # mob = self.current_monster_list.index(startswith_boolean_list)
            # mob = self.current_monster_list[startswith_boolean_list.index(1)]
            # mob = sorted_mob_list[startswith_boolean_list.index(1)]
            # mob = target
            if spell:
                self.socket_output.append('You cast a ' + spell + ' spell on the ' + mob + ' for 12 damage.\n\r')
            else:
                self.socket_output.append('You lash out and thump the ' + mob + ' for 8 damage.\n\r')

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
            if mob == 'acrobat':
                self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
            elif mob == 'juggler':
                if len(self.current_mud_area.area_exits) > 1:
                    self.mobflee(mob, str(self.current_mud_area.area_exits[1].exit_type.name))
                else:
                    self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
            elif mob == 'militia soldier':
                self.rng = (self.rng + 1) % 8
                if self.rng == 1 and self.char.hp > 47:
                    self.char.hp = self.char.hp - 47
                    self.socket_output.append('[' + str(self.char.hp) + ' H 27 M]: The militia soldier painfully head-butts you for 47 damage.\n\r')
                elif self.rng == 0:
                    self.mobdead(mob)
            elif mob == 'tabby cat':
                magentaprint("Fake rng: " + str(self.rng))
                self.rng = (self.rng + 1) % 5  # He only needs to hit you twice unless you heal super quick
                if self.rng == 4:
                    self.mobdead(mob)
                # elif self.rng == 1:
                #     self.char.hp = max(self.char.hp - 60, 0)
                #     self.socket_output.append('[%s H %s M]: The tabby cat painfully head-butts you for 60 damage.\n\r' % (self.char.hp, self.char.mp))
                #     if self.char.hp == 0:
                #         self.char.hp = 1
                #         self.socket_output.append("You are overwhelmed by the tabby cat's attack and you collapse!\n\r")
                elif not self.rng % 2:
                    dmg = self.char.hp - 2
                    self.char.hp = 2
                    self.socket_output.append('[%s H %s M]: The tabby cat painfully head-butts you for %s damage.\n\r' % (self.char.hp, self.char.mp, dmg))
                    # if self.char.hp == 0:
                    #     self.char.hp = 1
                    #     self.socket_output.append("You are overwhelmed by the tabby cat's attack and you collapse!\n\r")
                self.socket_output.append('[%s H %s M]: ' % (self.char.hp, self.char.mp))
            elif mob == 'kobold champion':
                self.rng = (self.rng + 1) % 4
                self.socket_output.append('[' + str(self.char.hp) + ' H 27 M]: The kobold champion throws a wild punch at you, but it misses.\n\r')
                if self.rng == 0:
                    self.socket_output.append('Your maul hammer shatters.\n\r')
                    self.char.equipment.weapon = ''
                    self.mobdead(mob)
            elif mob == 'large kobold':
                self.rng = (self.rng + 1) % 4
                self.socket_output.append('[' + str(self.char.hp) + ' H 27 M]: The large kobold throws a wild punch at you, but it misses.\n\r')
                if self.rng == 2:
                    self.socket_output.append('Your maul hammer breaks and you have to remove it.\n\r')
                    self.inventory.add('maul hammer')
                    self.char.equipment.weapon = ''
                elif self.rng == 0:
                    self.mobdead(mob)
            elif mob == 'kobold sentry':
                self.rng = (self.rng + 1) % 4
                self.socket_output.append('[' + str(self.char.hp) + ' H 27 M]: The kobold sentry throws a wild punch at you, but it misses.\n\r')
                if self.rng == 1:
                    self.socket_output.append('Your spear breaks and you have to remove it.\n\r')
                    self.char.equipment.seconded = ''
                elif self.rng == 0:
                    self.mobdead(mob)
            elif mob == self.actor.name:
                if self.actor.do_combat():
                    if self.actor.name in self.current_monster_list:
                        self.current_monster_list.remove(self.actor.name)
            # self.mobflee(mob, str(self.current_mud_area.area_exits[0].exit_type.name))
            else:
                self.rng = (self.rng + 1) % 3
                if self.rng == 0:
                    self.mobdead(mob)
        else:
            if spell:
                self.socket_output.append('They are not here.\n\r')
            else:
                self.socket_output.append('Attack what?\n\r')

    def get_mob_name(self, target):
        # if mob in self.current_monster_list:
        # startswith_boolean_list = [m.startswith(mob) for m in sorted_mob_list]
        # startswith_boolean_list = [m.startswith(mob) for m in sorted_mob_list]
        return self.get_full_name_of_target(target, sorted(self.current_monster_list))

    def get_full_name_of_target(self, target, alist):
        # list can be a mob list of an exit list for example        
        target_split = target.split(' ')
        target_word = target_split[0]

        if len(target_split) > 1 and re.match('\d+', target_split[1]):
            no = int(target_split[1])
        else:
            no = 1

        for full_mob in alist:
            m_split = full_mob.split(' ')
            if any([w.startswith(target_word) for w in m_split]):
                no = no-1
                if no == 0:
                    return full_mob
        return None

    def kill(self, mob):
        self.mob_combat(mob, 'You lash out and thump the ' + mob + ' for 8 damage.\n\r', 'Attack what?\n\r')

    def cast(self, spell, mob):
        self.mob_combat(mob, 'You cast a ' + spell + ' spell on the ' + mob + ' for 12 damage.\n\r', 'They are not here.\n\r')

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
        magentaprint('Go.expand_direction() error case.\n\r')
        return ''

