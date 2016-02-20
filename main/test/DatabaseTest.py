import unittest
from main.misc_functions import *
from main.data.MudMob import *
from main.data.MudItem import *

class data_functionsTest(unittest.TestCase):

    # def test_get_mob_locations_by_aura_and_level(self):
    #     #setup
    #     mls = MudMob.get_mobs_by_level_and_aura_ranges(6, 8, 6, 8)
    #     result = True

    #     for m in mls:
    #         print(str(m))

    #     self.assertEquals(True , result)

    def test_get_itemmodel_by_name(self):
        itemmodel = ItemTypeModel.get_by_name("weapon")

        self.assertEquals(itemmodel[0].name, "weapon")

    def test_get_itemstore_by_itemtype(self):
        items = MudItem.get_suitable_item_of_type("weapon", "blunt", 2)

        print(items)

        for i in items:
            print(str(i))

        self.assertEquals(True, True)
