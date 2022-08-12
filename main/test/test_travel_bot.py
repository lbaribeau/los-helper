
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest
from db.Database import *
from db.MudMap import MudMap

from mini_bots.travel_bot import TravelBot

class TestTravelBot(unittest.TestCase):
    def test_get_directions(self):
        self.assertIn(
            TravelBot(None,None,MudMap()).get_directions(2, 5), 
            [
                ['out','s'],
                ['out','south']
            ]
        )
