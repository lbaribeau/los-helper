
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest

from combat.mob_target_determinator import MobTargetDeterminator
from reactions.referencing_list import ReferencingList

class TestMobTargetDeterminator(unittest.TestCase):
    def test_on_mob_arrival_should_increment(self):
        mtd = MobTargetDeterminator()
        # def on_mob_arrival(self, old_target_reference, arrived_mobs, mob_list):
        result = mtd.on_mob_arrival('s', ['shopper'], ReferencingList(['shopper','spiv']))
        print('new result: ' + str(result))
        self.assertEqual('s 2', result)

    def test_on_mob_departure_should_decrement(self):
        mtd = MobTargetDeterminator()
        # result = mtd.on_mob_departure('s 2', 'shopper', ReferencingList(['spiv']))
        # (def on_mob_departure(self, old_target_reference, old_mob_list, departed_mob_ref):)
        result = mtd.on_mob_departure('s 2', ReferencingList(['shopper', 'spiv']), 'shopper')
        print('new result: ' + str(result))
        self.assertEqual('s', result)

    def test_bandit_arrives_vs_bandit_sentry(self):
        mtd = MobTargetDeterminator()
        #                     (self, old_target_reference, arrived_mobs, mob_list)
        # result = mtd.on_mob_arrival('bandit', ['bandit'], ReferencingList(['bandit','bandit sentry']))
        result = mtd.on_mob_arrival('bandit', ['bandit'], ReferencingList(['bandit','bandit sentry']))
        print('Should hit the bandit sentry: ' + str(result))
        self.assertTrue(result == 'bandit 2' or result == 'sentry')

    def test_on_mob_departure_should_decrement_when_1st_drunken_miner_leaves(self):
        mtd = MobTargetDeterminator()
        result = mtd.on_mob_departure('d 3', ReferencingList(['drunken miner', 'drunken miner', 'drunken miner']), 'd')
        print('new result: ' + str(result))
        self.assertEqual('d 2', result)

    def test_on_mob_departure_should_decrement_when_2nd_drunken_miner_leaves(self):
        mtd = MobTargetDeterminator()
        result = mtd.on_mob_departure('d 3', ReferencingList(['drunken miner', 'drunken miner', 'drunken miner']), 'd 2')
        print('new result: ' + str(result))
        self.assertEqual('d 2', result)
