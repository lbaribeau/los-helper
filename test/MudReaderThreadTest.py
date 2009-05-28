import unittest
from main.MudReaderThread import MudReaderThread
class MudReaderThreadTest(unittest.TestCase):


    def test_parse_inventory_list_shouldReturnItemTwice_whenThereAreTwoInInput(self):
        #setup
        input = "two leaf blades"
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(["leaf blade", "leaf blade"], result)



