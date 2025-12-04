
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest
import re
from reactions.referencing_list import ReferencingList
from reactions.Mobs import Mobs
import comm.RegexStore as R
from comm.Character import Character
from reactions.Cartography import Cartography
from comm.MudReaderHandler import MudReaderHandler
from comm.MudReaderThread import MudReaderThread

class TestMobs(unittest.TestCase):
    # You see The Floor Manager (E).
    # You attack The Floor Manager.
    # Your enemy, The Floor Manager has been defeated.
    # Your attack overwhelms The Floor Manager and he collapses!
    def test_remove_floor_manager_from_attacking(self):
        C=Character()
        # mobs=Mobs()
        mobs=C.mobs
        # regex=
        # match_arrived=re.match(R.mob_arrived[0],"You see The Floor Manager (E).")
        # C.mobs.list  = ReferencingList(Cartography.parse_monster_list("You see The Floor Manager (E)."))
        cartography=Cartography(MudReaderHandler(MudReaderThread(None,C,None),C),None,C)
        print("R.area[0] is {}".format(R.area[0]))
        # print("R.area[0] is {}".format(R.area[0]))
        # cartography.notify(R.area[0],re.match(R.area[0], "Holly Lane\n\nThis is Holly lane.\nObvious exits: south.\nYou see The Floor Manager (E)."))
        # cartography.notify(R.area[0],re.match(r"Test (regex)", "Holly Lane\n\nThis is Test regex.\nObvious exits: south.\nYou see The Floor Manager (E)."))
        cartography.notify(R.area[0],re.match(r"(Holly Lane) (b) (Obvious exits: south.) (You see The Floor Manager \(E\)\.)", "Holly Lane b Obvious exits: south. You see The Floor Manager (E)."))
        # mobs.notify(R.mob_arrived, match_arrived) # match.re is compiled
        # character={}
        # character.mobs
        self.assertTrue('Floor Manager' in mobs.list.list)
        # match_hit_you=re.match(R.mob_attacked[0], "The Floor Manager punches you for 10 damage.") # Didn't add it
        # mob_aggro_match=re.match(R.mob_aggro[0], "The Floor Manager attacks you.") # Let's do you_attack first
        aggro_match=re.match(R.you_attack[0], "You attack The Floor Manager.") # Let's do you_attack first
        mobs.notify(R.you_attack[0], aggro_match)
        print("Mobs list is {}".format(mobs.list.list))
        print("Mobs attacking is {}".format(mobs.attacking))
        self.assertTrue(mobs.list.list[0] in mobs.attacking) # Good we got this one to pass
        match_mob_died=re.match(R.ze_mob_died[0], "Your attack overwhelms The Floor Manager and he collapses!")
        mobs.notify(R.ze_mob_died, match_mob_died)
        self.assertTrue(len(mobs.list.list)==0)
        self.assertTrue(len(mobs.attacking)==0)
        return True

if __name__=='__main__':
    TestMobs().test_remove_floor_manager_from_attacking() # doesn't import