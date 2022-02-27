'''
Driver code to generate graph, using collab_dict data
'''

import pickle

from pprint import pprint 

import collabgraph

#GET DATA FROM collabmap_data

with open('data/collab.pickle', 'rb') as f:
    collab_dict = pickle.load(f)

pprint(collab_dict)

#CREATE GRAPH OBJECT WITH NETWORKX
collab_network = collabgraph.CollabNetwork(collab_dict)

# Position graph
parameters = {'iterations':100,
              'k':None}

position = collab_network.position_network(parameters)

#GRAPH WITH PLOTLY

collab_graph = collabgraph.CollabGraph()
collab_graph.draw_graph(collab_network, position)


'''
TODO

-Determine best parameters for position of nodes

-Let collabgraph inherit from networkx?


'''
