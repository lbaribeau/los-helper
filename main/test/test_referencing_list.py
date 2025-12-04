
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest

from reactions.referencing_list import ReferencingList

class TestReferencingList(unittest.TestCase):
    def test_bandit_added_to_bandit_sentry(self):
        # Should get ['bandit','bandit sentry']
        # (bandit is alphabetically before bandit sentry)
        L = ReferencingList(['bandit sentry'])
        L.add_from_list(['bandit'])
        print("L.list should be ['bandit','bandit sentry']: " + str(L.list))
        self.assertEqual(L.list, ['bandit','bandit sentry'])

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

    # def test_bandit_arrives_vs_bandit_sentry(self):
    #     mtd = MobTargetDeterminator()
    #     #                     (self, old_target_reference, arrived_mobs, mob_list)
    #     result = mtd.on_mob_arrival('bandit sentry', ['bandit'], ReferencingList(['bandit sentry','bandit']))
    #     print('Should be : ' + str(result))
