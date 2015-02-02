import unittest
from main.misc_functions import *
from main.data.MudMob import *

class data_functionsTest(unittest.TestCase):

    def test_get_mob_locations_by_aura_and_level(self):
        #setup
        mls = MudMob.get_mobs_by_level_and_aura_ranges(6, 8, 6, 8)
        result = True

        for m in mls:
            print(str(m))

        self.assertEquals(True , result)
