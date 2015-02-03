import unittest
from main.misc_functions import *

class misc_functionsTest(unittest.TestCase):

    def test_get_last_word(self):
        #setup
        print ("Testing get last word")
        input1 = "kk heather seller"
        expected_outcome = "seller"

        result = get_last_word(input1)

        self.assertEquals(expected_outcome , result)

    def test_get_shortest_array(self):
        arrays = [
            ["east", "west", "east", "west", "east", "west"],
            ["east", "west", "east", "west"],
            ["east", "west", "east"],
            ["east", "west", "east", "west"],
            ["east", "west", "east", "west",
            "east", "west", "east", "west",
            "east", "west", "east", "west",
            "east", "west", "east", "west",
            "east", "west", "east", "west",
            "east", "west", "east", "west",
            "east", "west", "east", "west"]
        ]

        result = get_shortest_array(arrays)

        self.assertEquals(arrays[2], result)