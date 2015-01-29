import sys, time, re
from data.Database import *
from data.MudMap import *

class FakeSocketOutput(object):
    def __init__(self, text=""):
        self.text = text

    def decode(self, format="", errors=""):
        return self.text

class FakeTelnetSocket(object):
    def __init__(self, mud_map):
        self.content = ["[90 H 17 M]"]
        self.mud_map = mud_map

        ##### CONTENT ######
        self.inventory_string = 'You have: an Elixir of Morinva, two black bags, a broom, a cabbage,\n two carrots, three cauliflowers, some chicken soup, three feathers, some furry mittens, three granite pot\nions, a grey cloak, a large bag, three large iron shields, two large maces, a large orcish sword, two mandibles, five philtre of perc\neption, some ring mail armour, some ring mail leggings, a scarlet potion, a sparkler, four tree roots.'
        self.whois_string = 'Player                Cls Gen [Lv]Title                      Age   Race      \n-----------------------------------------------------------------------------\nDerp                  Mon  M  [14]Enlightened Brother        16    Human\n'
        self.time_string = '                      Meditate   *READY*\n                         Touch   3:25 minutes remaining\n'
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
        if (command == "i"):
            self.content.append(self.inventory_string)
        elif (re.match("whois (.+?)", command)):
            self.content.append(self.whois_string)
        elif (re.match("time", command)):
            self.content.append(self.time_string)
        elif (re.match("c show", command)):
            self.content.append("You glow with a grey aura.\n")
        elif (re.match("genaid [\d]*", command)): #OUTPUT AN AREA
            M_obj = re.search("genaid ([\d]*)", command)
            area = Area.get_area_by_id(int(M_obj.group(1)))
            self.gen_area(area)
        elif (command == "l"):
            self.content.append(str(self.show_current_area()))
        elif (re.match("addmob .+", command)): #OUTPUT AN AREA
            M_obj = re.search("addmob (.+)", command)
            mob = str(M_obj.group(1))
            self.current_monster_list.append(mob)
            mob_arrived_string = "An " + mob + " just arrived.\n"
            self.content.append(mob_arrived_string)
        elif (re.match("mobflee .+? .+", command)):
            M_obj = re.search("mobflee (.+?) (.+)", command)
            mob = str(M_obj.group(1))
            direction = str(M_obj.group(2))
            flee_string = "The " + mob + " flees to the " + direction + ".\n"
            self.content.append(flee_string)
        elif (re.match("mobdead .+", command)):
            M_obj = re.search("mobdead (.+)", command)
            mob = str(M_obj.group(1))
            dead_string = "Your attack overwhelms the " + mob + " and he collapses!\nYour enemy, the " + mob + " has been defeated.\nYou gain 11 experience.\n"
            self.current_monster_list = []
            self.content.append(dead_string)
        elif (re.match("go .+", command)):
            M_obj = re.search("go (.+)", command)
            direction = str(M_obj.group(1))
            exit = ExitType(name=direction)
            mud_area = self.current_mud_area.get_area_to_from_exit(exit)
            self.gen_area(mud_area.area)


    def gen_area(self, area):
        self.current_mud_area = MudArea(area)
        #(.+?\n\r)((?:\n\r.+)*)?(\n\rObvious exits: .+?[\n\r]?.+?\.)\n\r(You see .+?[\n\r]?.+?\.)?[\n\r]?(You see .+?[\n\r]?.+?\.)?
        area_string = (area.name + "\n\r\n\r" +
                      #str(area.description) + "\n\r" +
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
        time.sleep(0.1)
        if len(self.content) is not 0:
            fso = FakeSocketOutput(self.content.pop(0))
            return fso
        else:
            time.sleep(1)
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

        self.tn.write("genaid 45") #lets start us in the chapel
        self.tn.write("addmob spiv") #most everything will fight this

        self.echoing = True

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



