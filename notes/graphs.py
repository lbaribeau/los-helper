import networkx as nx
g=nx.Graph()
g.add_node("Immigration Office")
g.add_node("Adventurer's Training Hall")
g.add_edge("Immigration Office","Adventurer's Training Hall", name="staircase")
print(g.nodes())
#['Immigration Office', "Adventurer's Training Hall"]
print(g.edges())
#[('Immigration Office', "Adventurer's Training Hall")]
g.edges()[0]
#('Immigration Office', "Adventurer's Training Hall")
g["Immigration Office"]["Adventurer's Training Hall"]
#{'name': 'staircase'}
g["Immigration Office"]["Adventurer's Training Hall"]["name"]
#'staircase'
g.neighbors("Adventurer's Training Hall")
#['Immigration Office']
import code; code.interact(local=locals())

