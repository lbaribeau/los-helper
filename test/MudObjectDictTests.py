import unittest
from main.data.GenericMudObject import *
from main.data.GenericMudList import *
from main.data.MudObjectDict import *

class MudObjectDict_functionsTest(unittest.TestCase):

    def simple_parser(self, string):
        return {string: GenericMudList([string])}

    def test_AddToDict_simple_parser(self):
        objs = MudObjectDict(self.simple_parser)

        objs.add("Name1")
        objs.add("Name2")

        result = len(objs.dictionary)

        self.assertEquals(result, 2)

    def test_GetCount(self):
        objs = MudObjectDict(self.simple_parser)

        objs.add("Name1")
        objs.add("Name2")

        result = objs.count()

        self.assertEquals(result, 2)