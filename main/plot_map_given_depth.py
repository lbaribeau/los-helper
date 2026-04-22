
import networkx
import matplotlib
# pyplot=matplotlib.pyplot
import matplotlib.pyplot as pyplot
from misc_functions import magentaprint

import copy
from matplotlib import pyplot
print("... db.Area..."); import db.Area
from db.MudArea import MudArea

class PlotNearNodes:
	def __init__(self, los_map):
		self.los_map = los_map # networkx DiGraph

	def plot(self, area_id=2, depth=6):
		# magentaprint("dir(self.los_map)")
		# magentaprint(dir(self.los_map))
		# # self.first_try()
		# # networkx.draw_networkx_edges(self.los_map) # missing required argment 'pos''
		# # networkx.draw_networkx_edges(self.los_map, networkx.spring_layout(self.los_map, seed=13648)) # scipy error
		# # networkx.draw(self.los_map) # gcf()._axstack isn't callable, but draw calls draw_networkx
		# # networkx.draw_networkx(self.los_map) # still need scipy for \networkx\convert_matrix.py line 874, in to_scipy_sparse_array (ok scipy was 42 MB)
		# networkx.draw_networkx(self.los_map, nodelist=[], alpha=0.7, width=0.1, edge_color='grey', font_size=6, arrows=False)
		# pyplot.tight_layout()
		# # pyplot.autoscale(axis='y', tight=True)
		# pyplot.autoscale(tight=True)
		# pyplot.ion()
		# pyplot.show()
		plot_near_nodes(self.los_map, area_id, depth)

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
		magentaprint(f"Depth {depth}")
		if depth <= 0:
		# if depth <= 0 or area_id in self.mini_graph:
			# magentaprint("Got to base case!")
			return 

		# self.mini_graph.add_node(area_id) # Could get double added I guess
			# No need to add nodes AND edges, just add edges
		for n in reference_graph.successors(area_id):
			# self.mini_graph.add_edge(area_id, n, label='test')
			mudarea = MudArea(db.Area.Area.get_area_by_id(area_id))
			exit_name = mudarea.get_exit_name_to_areaid(n)
			magentaprint(f"... From {area_id:4} ({mudarea.area.name}) (depth is {depth}), to get to {n:4}, go {exit_name}. ")
			if n == 1:
				magentaprint("... ... Got a \"1\" (Unmapped)")
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

def plot_near_nodes(los_map, area_id, depth):
	# Reference: Plotter.py
	magentaprint(" --- Entering plot_map_given_depth.plot_near_nodes() --- ")
	# [magentaprint(d) for d in dir(los_map)]
	# networkx.draw_networkx_edges(self.los_map) # missing required argment 'pos''
	# networkx.draw_networkx_edges(self.los_map, networkx.spring_layout(self.los_map, seed=13648)) # scipy error
	# networkx.draw(self.los_map) # gcf()._axstack isn't callable, but draw calls draw_networkx
	# networkx.draw_networkx(self.los_map) # still need scipy for \networkx\convert_matrix.py line 874, in to_scipy_sparse_array (ok scipy was 42 MB)

	# Some reference code from Plotter that works with edges and nodes a bit
	# los_map=copy.deepcopy(los_map)
	# # new_edges = [e for e in los_map.edges if e[0] in range(2,2655) and e[1] in range(2,2655)] # Reduces size
	# # new_nodes = [n for n in los_map.nodes if n in range(2,2655)]
	# # los_map.clear_edges()
	# los_map.clear()
	# los_map.add_edges_from(new_edges)
	# los_map.add_nodes_from(new_nodes)

    # chapel_aid= db.Area.Area.get_by_name("The Chapel of Healing").id
    # mini_graph=networkx.DiGraph()
    # mini_graph.add_node(area_id)
    # for i in range(depth)
	    # s = los_map.successors(area_id) 
	mini_graph = MyDigraphCopier(los_map, area_id, depth).mini_graph

	kamada_kawai_positions = networkx.drawing.kamada_kawai_layout(
	# kamada_kawai_positions = networkx.drawing.planar_layout(
	# kamada_kawai_positions = networkx.drawing.spring_layout(
		mini_graph,
		# dim=3, # For 3d
		# Edges are like springs
		# seed=0, # Consistent result
		# pos=pos
		# fixed=pos.keys()#[2,1258,1380,1050,120,1388, 1265, 698, 1621,215,28]
	) # returns positions (pos)

	pyplot.figure("plot_map_given_depth.py")

	networkx.draw_networkx(
		mini_graph, # Graph G
		# networkx.drawing.spring_layout(
		kamada_kawai_positions,
		# networkx.drawing.kamada_kawai_layout(
		# 	mini_graph,
		# 	# Edges are like springs
		# 	# seed=0, # Consistent result
		# 	# pos=pos
		# 	# fixed=pos.keys()#[2,1258,1380,1050,120,1388, 1265, 698, 1621,215,28]
		# ), # returns positions (pos)
		# pos={
		# networkx.drawing.spring_layout(mini_graph, dim=3), # vertices must be 2d with shape (M,2) not (2,3)
		nodelist    = [],  # (Don't plot nodes) ("Draw only specified nodes") (I guess no nodes are drawn, maybe the edges have labels)
		# Comment out, so, default node list is list(G)
		# edgelist    = [e for e in mini_graph.edges if e[0] != 1 and e[1] != 1][:100],
		edgelist    = [e for e in mini_graph.edges if e[0] != 1 and e[1] != 1], # Specifies edges to draw (don't draw edges to 1 (?) 1 is still on the map though, and labels)
		alpha       = 0.7, 
		width       = 0.2, 
		edge_color  = 'black', 
		font_size   = 7, 
		arrows      = False, # Did arrows=False before for entire map (plotter.py, command "plot_map")
		with_labels = True, # Node ids
		# labels = {id: title for id, title in db.Area.Area.get_by_}
		# labels = {id: db.Area.Area.get_area_by_id(id) for id, title in db.Area.Area.get_by_}
		# labels = {id: db.Area.Area.get_area_by_id(id) for id in list(mini_graph)} # Very slow db query likely? # Also interesting how I got the area title by accident!
		labels = {id: id for id in list(mini_graph)} # Very slow db query likely? # Also interesting how I got the area title by accident!
        # chapel_aid    = db.Area.Area.get_by_name("The Chapel of Healing").id
	)

	if True: # Exit labels
		networkx.draw_networkx_edge_labels(
			mini_graph,
			kamada_kawai_positions,
			edge_labels = networkx.get_edge_attributes(mini_graph, 'label'),
			bbox=dict(alpha=0, boxstyle='round,pad=.1',fc='white',ec='none'), # label bounding boxes are intended to prioritize being able to see the label but cover the graph
			label_pos=.667, # so they aren't centered (hopefully can see both directions)
			rotate=True,
			font_weight='light',
			font_family='sans-serif',
			alpha=.7,
			clip_on=False,
			horizontalalignment='center'
		)

	# for p in [_p for _p in pos.values() if _p :
	# for (n, p) in [(_n, _p) for (_n, _p) in pos.items() if _n<216]:
	# 	pyplot.plot(p[0],p[1],'ob',alpha=0.5)
	# pyplot.plot(0,0, 'ob', alpha=0.5)
	pyplot.tight_layout()
	# pyplot.autoscale(axis='y', tight=True)
	# Read networkx source for options (AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_...\LocalCache\local-packages\Python310\site-packages\networkx\nx_pyloab.py)
	pyplot.autoscale(tight=True)
	# pyplot.grid(which='major',color='#d4d4d4')
	# pyplot.grid(which='minor',color='#eaeaea')
	pyplot.ion()
	pyplot.show()
	magentaprint(" --- Exiting \"plot_map_given_depth.plot_near_nodes()\" (interactive is \"on\", just called \"show()\" --- ")
#plot_map(los_map)
