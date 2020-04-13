
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest

from combat.mob_target_determinator import MobTargetDeterminator
from reactions.referencing_list import ReferencingList

class TestMobTargetDeterminator(unittest.TestCase):
    # def test_on_mob_arrival_should_increment(self):
    #     mtd = MobTargetDeterminator()
    #     result = mtd.on_mob_arrival('s', ['shopper'], ReferencingList(['shopper','spiv']))
    #     print('new result: ' + str(result))
    #     self.assertEqual('s 2', result)

    # def test_on_mob_departure_should_decrement(self):
    #     mtd = MobTargetDeterminator()
    #     result = mtd.on_mob_departure('s 2', 'shopper', ReferencingList(['spiv']))
    #     print('new result: ' + str(result))
    #     self.assertEqual('s', result)

    def test_on_similar_mob_arrival(self):
        mtd = MobTargetDeterminator()
        result = mtd.on_mob_arrival('gno 3', ['gnoll mage'], ReferencingList(['gnoll mage', 'gnoll cook']))
        print('new result {}'.format(str(result)))
        self.assertEqual('gno 3', result)

    def test_on_similar_mob_arrival(self):
        mtd = MobTargetDeterminator()
        mob_list = ReferencingList(['gnoll mage', 'gnoll cook', 'gnoll spearsman'])
        result = mtd.on_mob_arrival('gno 2', ['gnoll cook'], mob_list)
        print('new result {}'.format(str(result)))
        self.assertEqual('gno 3', result)
