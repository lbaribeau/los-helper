
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest

#from combat.mob_target_determinator import MobTargetDeterminator
#from reactions.referencing_list import ReferencingList
from command.Inventory import Inventory
from fake.FakeTelnetHandler import FakeTelnetHandler
from comm.Character import Character
from misc_functions import magentaprint
from db.MudItem import MudItem

class TestInventory(unittest.TestCase):
    def test_two_sets_of_leggings(self):
        i = Inventory(
            FakeTelnetHandler(),
            Character()
        )
        i.set_inventory(
            "a buckler, some chicken soup, a large sack, some nails, some "+
            "paladins's plate armour, two sets of plate mail leggings, four scarlet potions, "+
            "four small flasks, a small restorative, some spectacles, a tatty "+
            "jacket, some title deeds, a whisky bottle."
        )
        leggings=i.get_first_reference('plate mail leggings')
        #magentaprint("Test inventory is " + str(i.to_dict()))
        #magentaprint("Test inventory is " + str(i))
        magentaprint("Test inventory reference is " +  leggings)
        self.assertTrue(
            leggings == 'plate 2'  or
            leggings == 'mail'     or
            leggings == 'mail 1'   or
            leggings == 'leggings' or
            leggings == 'leggings 1'
        )
        # This failed since the 's' got removed from 'two sets of ... leggings'
        # It was a plural s removal
        # Which should be done when something is a set of things
        # because the singular is still one set of the thing(s) and is still "plural"

    def test_get_reference_from_index(self):
        i = Inventory(
            FakeTelnetHandler(),
            Character()
        )
        # i.set_inventory(MudItem('maul hammer'), MudItem('maul hammer')) # Maybe it does this
        i.set_inventory('maul hammer', 'maul hammer')
        ref = i.get_reference_from_index(1),
        self.assertTrue(
            ref == 'maul 2' or
            ref == 'hammer 2')

    def test_get_broken(self):
        i = Inventory(
            FakeTelnetHandler(),
            Character()
        )
        i.set_inventory('maul hammer', 'maul hammer')
        i.list[1].is_usable=False
        ref = i.get_broken('maul hammer')
        self.assertTrue(
            ref == 'maul 2' or
            ref == 'hammer 2')

    def test_get_unbroken(self):
        i = Inventory(
            FakeTelnetHandler(),
            Character()
        )
        i.set_inventory('maul hammer', 'maul hammer')
        i.list[1].is_usable=False
        ref = i.get_unbroken('maul hammer')
        self.assertTrue(
            ref == 'maul' or
            ref == 'hammer')

