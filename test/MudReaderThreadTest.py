import unittest
from main.MudReaderThread import MudReaderThread
class MudReaderThreadTest(unittest.TestCase):


    def test_parse_inventory_list_charecterizationTest(self):
        #setup
        input = '''a candy cane, some cleaning rags, three large bags, a lasso, four
leaf blades, five silver chalices, a silver snuff box, five small
restoratives, five spears, five steel bottles, two stilletos.
'''
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(['candy cane', 'cleaning rags', 'large bag', 'large bag', 'large bag', 'lasso', 'leaf blade', 'leaf blade', 'leaf blade', 'leaf blade', 'silver chalice', 'silver chalice', 'silver chalice', 'silver chalice', 'silver chalice', 'silver snuff box', 'small restorative', 'small restorative', 'small restorative', 'small restorative', 'small restorative', 'spear', 'spear', 'spear', 'spear', 'spear', 'steel bottle', 'steel bottle', 'steel bottle', 'steel bottle', 'steel bottle', 'stilletos.', 'stilletos.'] , result)

    def test_parse_inventory_list_whenThereIsOneItem(self):
        #setup
        input = 'an item'
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(['item'], result)

    def test_parse_inventory_list_whenThereIsOneSet(self):
        #setup
        input = 'some pants'
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(['pants'], result)

    def test_parse_inventory_list_whenThereIsOneItemAndANewLine(self):
        #setup
        input = '''an
item'''
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(['item'], result)

    def test_parse_inventory_list_whenThereAreTwoItems(self):
        #setup
        input = 'two items'
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(['item', 'item'], result)

    def test_parse_inventory_list_shouldReturnExpandedList_whenThereAreTwoSets(self):
        #setup
        input = 'two sets of items'
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(['items', 'items'], result)

    def test_parse_inventory_list_whenThereAreFiveItems(self):
        #setup
        input = 'five items'
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(['item', 'item', 'item', 'item', 'item'], result)

    def test_parse_inventory_list_whenThereAreFiveSets(self):
        #setup
        input = 'five sets of items'
        #execute
        result = MudReaderThread().parse_inventory_list(input)
        #assert
        self.assertEquals(['items', 'items', 'items', 'items', 'items'], result)

#    def test_parse_inventory_list_steel_bottle_test(self):
#        
#        input =  "a hyena's ear, four javelins, a large sack, a sharp knife, two silver chalices, two small bags, a small knife, eight small restoratives, four spears, fourteen steel bottles, a steel mask."
#        
#        result = MudReaderThread().parse_inventory_list(input):
#        
#        self.assertEquals([')
        




