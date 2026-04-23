
import networkx
from misc_functions import magentaprint

print("... db.Area..."); import db.Area
from db.MudArea import MudArea

class MyDigraphCopier:
	def __init__(self, reference_graph, area_id, depth):
		self.mini_graph = networkx.DiGraph()
		# self.mini_graph.add_node(area_id)  # Assumes area_id is in reference_graph
		self.add_to_mini_graph(reference_graph, area_id, depth)
		for source_node, target_node, d in self.mini_graph.edges(data=True):
			# d is attribute dictionary of an edge
			d['label'] = 'nw' if d['label'] == 'northwest' else d['label']
			d['label'] = 'ne' if d['label'] == 'northeast' else d['label']
			d['label'] = 'sw' if d['label'] == 'southwest' else d['label']
			d['label'] = 'se' if d['label'] == 'southeast' else d['label']
			d['label'] = 'n' if d['label'] == 'north' else d['label']
			d['label'] = 's' if d['label'] == 'south' else d['label']
			d['label'] = 'e' if d['label'] == 'east' else d['label']
			d['label'] = 'w' if d['label'] == 'west' else d['label']
			d['label'] = 'd' if d['label'] == 'down' else d['label']
			d['label'] = 'u' if d['label'] == 'up' else d['label']
			d['label'] = 'ou' if d['label'] == 'out' else d['label']

	def add_to_mini_graph(self, reference_graph, area_id, depth):
		# Adds given node area_id to graph, adds edges from lookup from reference graph, and recursively adds connected nodes and their edges
		# magentaprint(f"Depth {depth}")
		magentaprint("")
		if depth <= 0:
		# if depth <= 0 or area_id in self.mini_graph:
			# magentaprint("Got to base case!")
			return 

		# self.mini_graph.add_node(area_id) # Could get double added I guess
			# No need to add nodes AND edges, just add edges
		list_set_list_neighbors = list(set(list(reference_graph.successors(area_id))+list(reference_graph.predecessors(area_id))))
		for n in list_set_list_neighbors:
			# self.mini_graph.add_edge(area_id, n, label='test')
			mudarea = MudArea(db.Area.Area.get_area_by_id(area_id))
			exit_name = mudarea.get_exit_name_to_areaid(n)
			# magentaprint(f"... From {area_id:4} ({mudarea.area.name}) (depth is {depth}), to get to {n:4}, go {exit_name}. ")
			magentaprint(f"... From {area_id:4} ({mudarea.area.name}), to get to {n:4}, go {exit_name}. ")
			# Prints are breadth-first, recursion is depth-first

		# for n in reference_graph.successors(area_id):
		# for n in list(set(reference_graph.successors(area_id)+reference_graph.predecessors(area_id))):
		# for n in list(set(list(reference_graph.successors(area_id))+list(reference_graph.predecessors(area_id)))):
		for n in list_set_list_neighbors:
			# self.mini_graph.add_edge(area_id, n, label='test')
			mudarea = MudArea(db.Area.Area.get_area_by_id(area_id))
			exit_name = mudarea.get_exit_name_to_areaid(n)
			if n == 1:
				magentaprint(f"... ... Got a \"1\" (Unmapped) ({exit_name} from {area_id})")
				continue # 1 is special node indicating unknown (don't map)
			if n in self.mini_graph:
				self.mini_graph.add_edge(area_id, n, label=exit_name) # !!! what a line of code... goes to DB to get whole MudArea which loops to retrieve exit
			else:
				self.mini_graph.add_edge(area_id, n, label=exit_name) # !!! what a line of code... goes to DB to get whole MudArea which loops to retrieve exit
				self.add_to_mini_graph(reference_graph, n, depth-1)
			# magentaprint(f"... From {area_id:4} ({mudarea.area.name}), go {exit_name} to get to {n:4}")
			# area_n = db.Area.Area.get_area_by_id(n)
			# area_n_title = area_n.name if hasattr(area_n, 'name') else None
			# magentaprint(f"... From {area_id:4} ({mudarea.area.name}), go {exit_name} to get to {n:4} ({area_n_title})")
			# This print is nice but it takes a step farther than we have already gone
			# Could also hit the predecessors