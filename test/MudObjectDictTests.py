import unittest
from main.data.MudItem import *
from main.data.GenericMudList import *
from main.data.MudObjectDict import *

class MudObjectDict_functionsTest(unittest.TestCase):

    # def simple_parser(self, generic_mud_object):
    #     return {generic_mud_object: GenericMudList([generic_mud_object])}

    def __init__(self, *args, **kwargs):
        super(MudObjectDict_functionsTest, self).__init__(*args, **kwargs)

        self.item_1 = MudItem("small lamp")
        self.item_1.map()
        self.item_1_mud_list = GenericMudList([self.item_1, self.item_1, self.item_1])
        self.item_1_count = len(self.item_1_mud_list)

        self.item_2 = MudItem("small knife")
        self.item_2.map()
        self.item_2_mud_list = GenericMudList([self.item_2, self.item_2, self.item_2])
        self.item_2_count = len(self.item_2_mud_list)

        self.item_3 = MudItem("iron ring")
        self.item_3.map()
        self.item_3_mud_list = GenericMudList([self.item_3])
        self.item_3_mud_count = len(self.item_3_mud_list)

        self.item_4 = MudItem("small sword")
        self.item_4.map()
        self.item_4_mud_list = GenericMudList([self.item_4])
        self.item_4_mud_count = len(self.item_4_mud_list)

        self.obj_dict = {
                         self.item_4 : self.item_4_mud_list,
                         self.item_2 : self.item_2_mud_list,
                         self.item_3 : self.item_3_mud_list,
                         self.item_1 : self.item_1_mud_list
                        }
        
        self.expected_unique_references = ["small 7", "small 6", "small 5", "small 4", "small 3", "small 2", "small 1", "iron 1"]
        self.exception_list = [self.item_1]
        self.expected_unique_references_sans_exception = ["small 7", "small 3", "small 2", "small 1", "iron 1"]

    def test_GetCount(self):
        objs = MudObjectDict()

        objs.add(self.obj_dict)

        count_result = objs.count()
        len_result = len(objs)

        self.assertEquals(count_result, len_result)

    def test_GetCountOfBolos(self):
        objs = MudObjectDict()

        objs.add(self.obj_dict)

        count_result = objs.count(self.item_2)

        self.assertEquals(count_result, self.item_2_count)

    def test_RemoveFromDict(self):
        objs = MudObjectDict()

        objs.add(self.obj_dict) #3 bolo, 1 ring

        #remove 1 bolo from the list!
        item_2_mud_list = GenericMudList([self.item_2])
        obj_dict = {self.item_2 : item_2_mud_list}

        pre_remove_len = len(objs)

        objs.remove(obj_dict)
        # magentaprint(objs, False)

        result = len(objs)

        self.assertEquals(result, (pre_remove_len - len(item_2_mud_list)))

    def test_GetUniqueReferences(self):
        objs = MudObjectDict()

        objs.add(self.obj_dict)

        result = objs.get_unique_references()

        self.assertEquals(result, self.expected_unique_references)

    def test_GetUniqueReferencesSansExceptions(self):
        objs = MudObjectDict()

        objs.add(self.obj_dict)

        result = objs.get_unique_references(self.exception_list)

        self.assertEquals(result, self.expected_unique_references_sans_exception)

