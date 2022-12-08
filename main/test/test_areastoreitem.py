
# http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
import unittest
# import main
# from main import los_helper
from db import AreaStoreItem
# import main
# from main.db import AreaStoreItem

class TestAreaStoreItem(unittest.TestCase):
    def test_get_by_item_type_and_level_max(self):
        AreaStoreItem().test_get_by_item_type_and_level_max(model_name, data_name, level_max=1)
        mtd = MobTargetDeterminator()
        result = mtd.on_mob_arrival('s', ['shopper'], ReferencingList(['shopper','spiv']))
        print('new result: ' + str(result))
        self.assertEqual('s 2', result)

    # def test_on_mob_departure_should_decrement(self):
    #     mtd = MobTargetDeterminator()
    #     result = mtd.on_mob_departure('s 2', 'shopper', ReferencingList(['spiv']))
    #     print('new result: ' + str(result))
    #     self.assertEqual('s', result)

print("Hello")
TestAreaStoreItem().test_get_by_item_type_and_level_max()

