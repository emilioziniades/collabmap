import pickle

import plotly.graph_objects as go
import networkx as nx

import collabmap

#GET DATA FROM collabmap_data

with open('collab.pickle', 'rb') as f:
    collab_dict = pickle.load(f)

#CREATE GRAPH OBJECT
G = nx.Graph()

#POPULATE GRAPH WITH NODES AND EDGES 

#Add nodes
for artist, collaborators in collab_dict.items():

    for artist1, collaborators1 in collaborators.items():
        
        for artist2, collaborators2 in collaborators1.items():

            G.add_node(artist2.name, size=4)

        G.add_node(artist1.name, size= 8)

    G.add_node(artist.name, size=11)

#Add edges
for artist, collaborators in collab_dict.items():

    for artist1, collaborators1 in collaborators.items():

        for artist2, collaborators2 in collaborators1.items():
            G.add_edge(artist1.name, artist2.name, weight= artist2.parent_collab_count*2)

        G.add_edge(artist.name, artist1.name, weight= artist1.parent_collab_count*2)

 

#Position graphs and edges
position = nx.spring_layout(G, scale= 4, k=0.3, iterations=60)

#GRAPH WITH PLOTLY

#Create instance of map
collabgraph = collabmap.CollabGraph() 

#Create node trace and edge traces
node_trace = collabgraph.make_node_trace(G, position)
edge_traces = collabgraph.make_edge_traces(G, position)

# Create figure
fig= go.Figure(layout= collabgraph.layout)

# Add node trace and add all edge traces
fig.add_trace(node_trace)
for edge_trace in edge_traces:
    fig.add_trace(edge_trace)

fig.show()