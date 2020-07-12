'''
Driver code to generate graph, using collab_dict data
'''

import pickle

import networkx as nx
import plotly.graph_objects as go

import collabgraph

#GET DATA FROM collabmap_data

with open('collab.pickle', 'rb') as f:
    collab_dict = pickle.load(f)

main_artist = list(collab_dict.keys())[0].name


#CREATE GRAPH OBJECT WITH NETWORKX
G = nx.Graph()

#POPULATE GRAPH WITH NODES AND EDGES

#Add nodes and edges recursively
collabgraph.make_nodes(collab_dict, G)
collabgraph.make_edges(collab_dict, G)

#Resize nodes
collabgraph.resize_nodes(G, main_artist)

#Position graphs and edges
position = nx.spring_layout(G, scale=6, k=0.3, iterations=60)

#GRAPH WITH PLOTLY

#Create instance of map
collabgraph = collabgraph.CollabGraph()

# Create node traces, edge traces and add to figure
node_trace = collabgraph.make_node_trace(G, position)
edge_traces = collabgraph.make_edge_traces(G, position)

# Create figure
fig = go.Figure(layout=collabgraph.layout)

# Add node trace and add all edge traces
collabgraph.add_nodes_and_edges_traces(node_trace, edge_traces, fig)


fig.show()


'''
TODO

-Determine best parameters for position of nodes


'''
