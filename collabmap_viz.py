import json

from pprint import pprint
import plotly.graph_objects as go
import networkx as nx

import collabmap

#GET DATA FROM collabmap_data

with open('test.json', 'r') as f:
    test_dict = json.load(f)

main_artists = []
collaborator_list = []

for key, value in test_dict.items():

    main_artists.append(key)

    for collaborator in value:
        collaborator_list.append(collaborator)

collaborator_list = set(collaborator_list)

#CREATE GRAPH OBJECT
G = nx.Graph()

#POPULATE GRAPH WITH NODES AND EDGES 

#Add nodes
G.add_nodes_from(collaborator_list, size= 4)
G.add_nodes_from(main_artists, size= 8)
G.add_node('Dope Saint Jude', size = 11)

#Add edges
for artist, collaborators in test_dict.items():
    for collaborator, count in collaborators.items():
        G.add_edge(artist, collaborator, weight= count*2)

#Position graphs and edges
position = nx.spring_layout(G, scale= 4, k=0.5, iterations=60)


#GRAPH WITH PLOTLY

#Create instance of map
CM = collabmap.CollabGraph() 

#Create node trace and edge traces
node_trace = CM.make_node_trace(G, position)
edge_traces = CM.make_edge_traces(G, position)

# Create figure
fig= go.Figure(layout= CM.layout)

# Add all edge traces, and add node trace
for edge_trace in edge_traces:
    fig.add_trace(edge_trace)
fig.add_trace(node_trace)

fig.show()