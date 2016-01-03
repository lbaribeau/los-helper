import unittest, re
from main.misc_functions import *
class MudReaderThreadTest(unittest.TestCase):


    def test_parse_inventory_list_charecterizationTest(self):
        area = """/---------------------------------------------------------------------------\
|    The Flint Engine version 1.9.9           Developed by Shihan, Kaedan   |
|    Derived from Mordor V4.06 by Brooke Paul & Brett Vickers               |
|                                                                           |
|    Website   : www.landsofstone.org                                       |
|    Game      : mud.landsofstone.org                                       |
|    Scenarios : type 'help credits' in-game to view details                |
|    Connection problems? email andyb@creative-realms.net with details.     |
|                                                                           |
|                          lands of stone v(0.86.8)                         |
|                                                                           |
|                                 Welcome!                                  |
|                                                                           |
\---------------------------------------------------------------------------/

Please enter name: Please enter password: 
### Herp the Human Apprentice just entered the Lands of Stone.

Town Hall Lobby

The entrance is quite narrow, but long. It doesn't seem busy though.
The initial appearance is of a place which is not much in use and the
dust everywhere seems to support that point of view. A small window
has a notice saying to wait in the room east for service, but as far
as you can tell there isn't anyone behind the window at all.
Obvious exits: east, doors, out.
You see a beggar, a tax inspector.
"""
        area = area.replace("\n", "\n\r")

        area_regex = "(?s)(?:(?:.+?Stone\.\n\r|.+?healed\.\n\r|.+?\]:\s+?)\n\r)?(^[A-Z].+?)\n\r\n\r(?:(.+?)\n\r)?(Obvious exits: .+?\.)\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?"
        area_regex = re.compile(r"(?:(?:.+?Stone\.\n\r|.+?healed\.\n\r|.+?\]:\s+?)\n\r)?([A-Z].+?)\n\r\n\r(?:(.+?)\n\r)?(Obvious exits: .+?\.)\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?", re.DOTALL|re.MULTILINE)
        M_obj = re.search(area_regex, area)

        # magentaprint(M_obj.group(0), False, False, True)

        for match in M_obj.groups():
            magentaprint(match, False)

        result = True

        self.assertEquals(True , result)



