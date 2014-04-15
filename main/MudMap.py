import networkx as nx
from Database import *

class MudArea():
	area = None
	area_exits = []

	def __init__(self, area, exits):
		self.area = area
		self.exits = exits

class MudMap():
	los_map = None

	def __init__(self):
		self.los_map = nx.DiGraph()
		self.populate_map()

	def populate_map(self):
		areas = Area.select()
		area_exits = AreaExit.select()

		for area in areas:
			self.los_map.add_node(area.id)

		for area_exit in area_exits:
			area_to_id = -1 #this is a marker for a null / unexplored area
			area_is_useable = True
			if (area_exit.area_to is not None):
				area_to_id = area_exit.area_to.id
				area_is_useable = area_exit.is_useable

			if area_is_useable: #don't add unusable areas to the graph
				name = area_exit.exit_type.name
				self.los_map.add_edge(area_exit.area_from.id,
					area_to_id,
					name=name)

	def to_string(self):
		return str(self.los_map.nodes()) + "\n\n" + str(self.los_map.edges())

	def get_path(self, start_area_id, end_area_id):
		node_path = nx.shortest_path(self.los_map,source=start_area_id,target=end_area_id)
		edge_path = []

		i = 0
		while i < (len(node_path) - 1):
			cur_edge = self.los_map.get_edge_data(node_path[i], node_path[i+1])

			edge_path.append(cur_edge['name'])
			i += 1

		return edge_path

	def get_nearest_unexplored_path(self, start_area_id):
		return self.get_path(start_area_id, -1)
