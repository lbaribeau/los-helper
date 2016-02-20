
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest

from mini_bots.travel_bot import TravelBot

class TestTravelBot(unittest.TestCase):
    def test_get_directions(self):
        directions = TravelBot().get_directions(map, 2, 5)
        self.assertEqual(directions, 'out','s')
