
import networkx
import matplotlib
# pyplot=matplotlib.pyplot
import matplotlib.pyplot as pyplot
from misc_functions import magentaprint

import copy
from matplotlib import pyplot
print("... db.Area..."); import db.Area
from db.MudArea import MudArea

from plots.MyDigraphCopier import MyDigraphCopier

from mpl_toolkits.mplot3d import Axes3D

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
	# mini_graph = MyDigraphCopier(los_map, area_id, depth).mini_graph
	mini_graph = MyDigraphCopier(los_map, area_id, depth).mini_graph.to_undirected(as_view=True) 
	# Saying ok treat unidirectional edges the same... also, no need to modify the graph, just need a view of this
	# So each edge isn't double plotted

	kamada_kawai_positions = networkx.drawing.kamada_kawai_layout(
	# kamada_kawai_positions = networkx.drawing.spring_layout(
		mini_graph,
		dim=3, # For 3d
		# Edges are like springs
		# seed=0, # Consistent result
		# pos=pos
		# fixed=pos.keys()#[2,1258,1380,1050,120,1388, 1265, 698, 1621,215,28]
	) # returns positions (pos)

	pyplot.figure("plot_map_given_depth_3d.py")
	pyplot.cla() # clear axis
	# pyplot.figure()
	ax=pyplot.gcf().add_subplot(111, projection='3d')
	x=0
	y=1
	z=2
	for edge in mini_graph.edges:
		ax.plot(\
			# Plot is taking
			# [x1, x2],
			# [y1, y2],
			# [z1, z2]
			# edge[0] and edge[1] are each nodes that have positions in kamada_kawai
			[kamada_kawai_positions[edge[0]][x], kamada_kawai_positions[edge[1]][x]],
			[kamada_kawai_positions[edge[0]][y], kamada_kawai_positions[edge[1]][y]],
			[kamada_kawai_positions[edge[0]][z], kamada_kawai_positions[edge[1]][z]],
			c='#111111',
			alpha=0.6,
			linewidth=1)

	if True:
		# Plotting nodes don't look great and really slow it down... just plot the edges
		# Ok well they look ok but really slow it down
		for node, coords in kamada_kawai_positions.items():
			# ax.scatter(coords[0], coords[1], coords[2], c='blue', s=20)
			# ax.scatter(coords[0], coords[1], coords[2], alpha=0.5, c='grey')
			# ax.scatter(coords[0], coords[1], coords[2], alpha=0.3, c='black', s=1)
			ax.scatter(coords[0], coords[1], coords[2], alpha=0.6, c='#111111', s=1)
			# label = db.Area.Area.get_area_by_id(node)
			# ax.text(coords[0], coords[1], coords[2], node, size=7)

	ax.set_xticklabels([])
	ax.set_yticklabels([])
	ax.set_zticklabels([])
	pyplot.subplots_adjust(left=0, bottom=0, right=1, top=1)
	ax.set_axis_off()

	# pyplot.show()

	# networkx.draw_networkx(
	# 	mini_graph, # Graph G
	# 	# networkx.drawing.spring_layout(
	# 	kamada_kawai_positions,
	# 	# networkx.drawing.kamada_kawai_layout(
	# 	# 	mini_graph,
	# 	# 	# Edges are like springs
	# 	# 	# seed=0, # Consistent result
	# 	# 	# pos=pos
	# 	# 	# fixed=pos.keys()#[2,1258,1380,1050,120,1388, 1265, 698, 1621,215,28]
	# 	# ), # returns positions (pos)
	# 	# pos={
	# 	# networkx.drawing.spring_layout(mini_graph, dim=3), # vertices must be 2d with shape (M,2) not (2,3)
	# 	# nodelist    = [],  # (Don't plot nodes) ("Draw only specified nodes") (I guess no nodes are drawn, maybe the edges have labels)
	# 	# Comment out, so, default node list is list(G)
	# 	# edgelist    = [e for e in mini_graph.edges if e[0] != 1 and e[1] != 1][:100],
	# 	edgelist    = [e for e in mini_graph.edges if e[0] != 1 and e[1] != 1], # Specifies edges to draw (don't draw edges to 1 (?) 1 is still on the map though, and labels)
	# 	alpha       = 0.8, 
	# 	width       = 0.2, 
	# 	edge_color  = 'black', 
	# 	font_size   = 7, 
	# 	arrows      = True, # Did False here for entire map
	# 	with_labels = True,
	# 	# labels = {id: title for id, title in db.Area.Area.get_by_}
	# 	# labels = {id: db.Area.Area.get_area_by_id(id) for id, title in db.Area.Area.get_by_}
	# 	labels = {id: db.Area.Area.get_area_by_id(id) for id in list(mini_graph)} # Very slow db query likely? # Also interesting how I got the area title by accident!
    #     # chapel_aid    = db.Area.Area.get_by_name("The Chapel of Healing").id
	# )
	# networkx.draw_networkx_edge_labels(
	# 	mini_graph,
	# 	kamada_kawai_positions,
	# 	edge_labels = networkx.get_edge_attributes(mini_graph, 'label')
	# )

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

	# Could try ax.plot_wireframe()
	# Google prompt: "is there a way in pyplot to tell matplotlib to slowly spin the 3d plot instead of me having to mouse drag it"
	# for angle in range(0, 360):
	#     ax.view_init(
	#     	elev = 10, 
	#     	azim = angle)
	#     pyplot.draw()
	#     pyplot.pause(0.02) # Controls the "spin" speed

	magentaprint(" --- Exiting \"plot_map_given_depth.plot_near_nodes()\" (interactive is \"on\", just called \"show()\" --- ")
#plot_map(los_map)
