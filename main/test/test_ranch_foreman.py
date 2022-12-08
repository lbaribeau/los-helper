
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest

from combat.mob_target_determinator import MobTargetDeterminator
from reactions.referencing_list import ReferencingList

class TestRanchForeman(unittest.TestCase):
    def test_should_target_when_theres_caps(self):
        reflist = ReferencingList()
        reflist.add('Rancher Plover')
        reflist.add('ranch foreman')
        result = reflist.get_reference('ranch foreman')
        print('Should be ranch 2: ' + result)
        self.assertTrue(result in ['ranch 2', 'foreman'])
