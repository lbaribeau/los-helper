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