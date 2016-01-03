
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest

# import main
# from main import los_helper

from combat.mob_target_determinator import MobTargetDeterminator
from reactions.referencing_list import ReferencingList
# import los_helper
# from main.misc_functions import magentaprint

class TestMobTargetDeterminator(unittest.TestCase):
    def test_silly(self):
        self.assertEqual(True, True)

    def test_on_mob_arrival_should_increment(self):
        mtd = MobTargetDeterminator()
        result = mtd.on_mob_arrival('s', ['shopper'], ReferencingList(['shopper','spiv']))
        print('new result: ' + str(result))
        self.assertEqual('s 2', result)

    def test_on_mob_departure_should_decrement(self):
        mtd = MobTargetDeterminator()
        result = mtd.on_mob_departure('s 2', 'shopper', ReferencingList(['spiv']))
        print('new result: ' + str(result))
        self.assertEqual('s', result)

    # def test_fail(self):
    #     self.assertEquals(True, False)
