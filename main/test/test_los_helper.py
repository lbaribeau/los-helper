
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest

# import main
# from main import los_helper

class TestLosHelper(unittest.TestCase):
    def setUp(self):
        print("Hello World!")

    def test_silly(self):
        self.assertEqual('foo'.upper(), 'FOO')

# unittest.main()

