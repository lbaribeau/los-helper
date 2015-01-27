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
        self.time_string = '                      Meditate   *READY*\n                         Touch   3:25 minutes remaining'
        self.current_area = ""
        self.current_monster_list = []

        self.fso = FakeSocketOutput()

    def connect(host="", port=""):
        #connection string
        print ("Connected to FakeTelnetSocket!")

    def write(self, command):
        #re.match("bot ?$|bot [0-9]+$", user_input)
        #M_obj = re.search("[0-9]+", user_input)
        if (command == "i"):
            self.content.insert(0, self.inventory_string)
        elif (re.match("whois (.+?)", command)):
            self.content.insert(0, self.whois_string)
        elif (re.match("time", command)):
            self.content.insert(0, self.time_string)
        elif (re.match("c show", command)):
            self.content.insert(0, "You glow with a grey aura.\n")
        elif (re.match("genaid [\d]*", command)): #OUTPUT AN AREA
            M_obj = re.search("genaid ([\d]*)", command)
            area = Area.get_area_by_id(int(M_obj.group(1)))


            #(.+?\n\r)((?:\n\r.+)*)?(\n\rObvious exits: .+?[\n\r]?.+?\.)\n\r(You see .+?[\n\r]?.+?\.)?[\n\r]?(You see .+?[\n\r]?.+?\.)?
            area_string = (area.name + "\n\r\n\r" +
                          str(area.description) + "\n\r" +
                          "Obvious exits: arched door, out, silver portal, chamber.")

            magentaprint(str(self.current_monster_list),False)

            self.current_area = area_string

            self.content.insert(0, str(self.show_current_area()))
        elif (command == "l"):
            self.content.insert(0, str(self.show_current_area()))
        elif (re.match("addmon .+", command)): #OUTPUT AN AREA
            M_obj = re.search("addmon (.+)", command)
            mob = str(M_obj.group(1))
            self.current_monster_list.insert(0, mob)

            mob_arrived_string = "An " + mob + " just arrived.\n"
            self.content.insert(0, mob_arrived_string)
        elif (re.match("mobflee .+", command)):
            M_obj = re.search("mobflee (.+)", command)
            mob = str(M_obj.group(1))
            flee_string = "The " + mob + " flees to the alley.\n"
            self.content.insert(0, flee_string)

    def show_current_area(self):
        area_string = self.current_area

        if len(self.current_monster_list) is not 0:
            area_string += "\n\rYou see "

            for mob in self.current_monster_list:
                area_string += "a " + mob

            area_string += "."

        return area_string + "\n\r"

    def read_some(self):
        time.sleep(1)
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
        self.tn.write("addmon spiv") #most everything will fight this

        self.echoing = False

    def write(self, command):
        if self.echoing:
            print ('{' + command + '}\r')
    
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



