
import unittest
from db.Database import *
from db.MudMap import MudMap

class TestMap(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.m = MudMap()

	def test_pawn_shop(self):
		# These tests use hard coded chapel area id (2)
		self.assertIn(self.m.get_path_to_nearest_pawn_shop(2),
			[
				['out','south','west','west','west','south','south','shop'],
				['out','s','w','w','w','s','s','shop']
			]
		)
	def test_smithy(self):
		self.assertIn(self.m.get_path_to_nearest_smithy(2),
			[
				['out','south','east','south','south','south','west','gate','south','southeast','southeast','east','east','east','southeast','southeast','southeast','south','south','south','south','south','south','south','south','east','smithy'],
				['out','s','e','s','s','s','w','gate','s','se','se','e','e','e','se','se','se','s','s','s','s','s','s','s','s','e','smithy']
			]
		)
	def test_tip(self):
		self.assertIn(self.m.get_path_to_nearest_tip(2),
			[
				['out', 'south', 'east', 'east', 'east', 'south', 'south', 'tip'],
				['out', 's', 'e', 'e', 'e', 's', 's', 'tip']
			]
		)
