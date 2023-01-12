
import networkx
import matplotlib
# pyplot=matplotlib.pyplot
import matplotlib.pyplot as pyplot
from misc_functions import magentaprint

class Plotter:
	def __init__(self, los_map):
		self.los_map = los_map # networkx DiGraph

	def plot_map(self):
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
		plot_map(self.los_map)

import copy
from matplotlib import pyplot
def plot_map(los_map):
	# I get an interactive session and edit/copy/paste this function
	magentaprint("dir(self.los_map)")
	magentaprint(dir(los_map))
	# networkx.draw_networkx_edges(self.los_map) # missing required argment 'pos''
	# networkx.draw_networkx_edges(self.los_map, networkx.spring_layout(self.los_map, seed=13648)) # scipy error
	# networkx.draw(self.los_map) # gcf()._axstack isn't callable, but draw calls draw_networkx
	# networkx.draw_networkx(self.los_map) # still need scipy for \networkx\convert_matrix.py line 874, in to_scipy_sparse_array (ok scipy was 42 MB)
	los_map=copy.deepcopy(los_map)
	# new_edges = [e for e in los_map.edges if e[0]!=1 and e[1]!=1]
	# new_edges = [e for e in los_map.edges if e[0] in range(2,2655) and e[1] in range(2,2655)] # Reduces size
	new_edges = [e for e in los_map.edges if e[0] in range(2,2655) and e[1] in range(2,2655)] # Reduces size
	new_nodes = [n for n in los_map.nodes if n in range(2,2655)]
	# los_map.clear_edges()
	los_map.clear()
	los_map.add_edges_from(new_edges)
	los_map.add_nodes_from(new_nodes)
	pos = {
		# 2    : (   0,    0), # Chapel
		# 28   : (0.3, 1), # North gate
		# 120  : (-1, -1), # Willan's Amethyst pawn shop
		# 215  : (11, 6), # Olarma 140
		# 1258 : ( 7, -7), # Medic centre
		# 1380 : (-5, -8), # Cheryn
		# 1050 : (   0, -8), # Castle
		# 1388 : (-6, -7),  # Harck's amber pawnshop
		# 1265 : (11, -11), # Horbuk
		# 698  : (-20, -5), # Thereze 186
		# 1621 : (-10, 10) # Shaldena 358
		# # 977 : (-20, 20) # Ha'Chans 977
		2    : (0,   0), # Chapel
		28   : (-2, 3), # North gate
		120  : (-3, -2), # Willan's Amethyst pawn shop
		215  : (30, 5), # Olarma 140
	}
	networkx.draw_networkx(
		los_map, # Ok we need to edit los_map
		networkx.drawing.kamada_kawai_layout(los_map
		# networkx.drawing.spring_layout(
			# Edges are like springs
			# los_map,
			# seed=0, # Consistent result
			# pos=pos
			# fixed=pos.keys()#[2,1258,1380,1050,120,1388, 1265, 698, 1621,215,28]
		),
		# pos={
		# networkx.drawing.spring_layout(los_map, dim=3), # vertices must be 2d with shape (M,2) not (2,3)
		nodelist    = [],  # (Don't plot nodes)
		# edgelist    = [e for e in los_map.edges if e[0] != 1 and e[1] != 1][:100],
		edgelist    = [e for e in los_map.edges if e[0] != 1 and e[1] != 1],
		alpha       = 0.8, 
		width       = 0.2, 
		edge_color  = 'black', 
		font_size   = 6, 
		arrows      = False,
		with_labels = True)
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
#plot_map(los_map)

	def first_try(self):
		# G = networkx.random_k_out_graph(10, 3, 0.5, seed=13648)
		G           = self.los_map
		pos         = networkx.spring_layout(G, seed=13648) # no module named 'scipy'
		M           = G.number_of_edges()
		# edge_colors = range(2, M+2)
		# node_sizes  = [3 + 10 * i for i in range(len(G))]

		nodes = networkx.draw_networkx_nodes(
			G, 
			pos, 
			# node_size  = node_sizes, 
			# node_color = "indigo"
		)

		edges = networkx.draw_networkx_edges(
		    G,
		    pos,
		    # node_size  = node_sizes,
		    # arrowstyle =  "->",
		    # arrowsize  = 10,
		    # edge_color = edge_colors,
		    # edge_cmap  = pyplot.cm.plasma,
		    # width      = 2,
		)

		for i in range(M):
		    edges[i].set_alpha((5+i)/(M+4))

		# patches = matplotlib.collections.PatchCollection(edges, cmap=pyplot.cm.plasma)
		patches = matplotlib.collections.PatchCollection(edges)
		patches.set_array(edge_colors)
		pyplot.gca().set_axis_off()
		pyplot.colorbar(patches, ax=pyplot.gca())
		pyplot.show()

		#https://networkx.org/documentation/stable/auto_examples/drawing/plot_directed.html

	# pyplot.plot(7,-7, 'ob', alpha=0.5)
	# pyplot.plot(-5,-8, 'ob', alpha=0.5)
	# pyplot.plot(0,-8, 'ob', alpha=0.5)
	# pyplot.plot(-1,-1, 'ob', alpha=0.5)
	# pyplot.plot(-6,-7, 'ob', alpha=0.5)
	# pyplot.plot(11,-11, 'ob', alpha=0.5)
	# pyplot.plot(-20,-5, 'ob', alpha=0.5)
	# pyplot.plot(-10,10, 'ob', alpha=0.5)
	# pyplot.plot(11,6, 'ob', alpha=0.5)
	# pyplot.plot(0.3,1, 'ob', alpha=0.5)