import json

import plotly.graph_objects as go
import networkx as nx

#GET DATA FROM SPOTIFY

with open('test.json', 'r') as f:
    test_dict = json.load(f)

main_artist = list(test_dict.keys())[0]
collaborators = list(test_dict[main_artist].keys())

#CREATE GRAPH OBJECT

G = nx.Graph()

#POPULATE GRAPH 

G.add_node(main_artist, size= 5)
G.add_nodes_from(collaborators, size= 3)

for collaborator in collaborators:
    G.add_edge(main_artist, collaborator, weight= test_dict[main_artist][collaborator]*2)

position = nx.spring_layout(G)

#CREATE NODE TRACE

node_trace = go.Scatter(x         = [],
                        y         = [],
                        text      = [],
                        textposition = "top center",
                        textfont_size = 10,
                        mode      = 'markers+text',
                        hoverinfo = 'none',
                        marker    = dict(color = [],
                                         size  = [],
                                         line  = None))

# For each node, get the position and size and add to the node_trace
for node in G.nodes():
    x, y = position[node]
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    node_trace['marker']['color'] += tuple(['cornflowerblue'])
    node_trace['marker']['size'] += tuple([5*G.nodes()[node]['size']])
    node_trace['text'] += tuple(['<b>' + node + '</b>'])

#CREATE EDGE TRACE

# Custom function to create an edge between node x and node y, with a given text and width
def make_edge(x, y, text, width):
    return  go.Scatter(x         = x,
                       y         = y,
                       line      = dict(width = width,
                                        color = 'cornflowerblue'),
                       hoverinfo = 'text',
                       text      = ([text]),
                       mode      = 'lines')


# For each edge, make an edge_trace, append to list
edge_trace = []
for edge in G.edges():
    
    print(edge)

    artist_1= edge[0]
    artist_2= edge[1]
    x0, y0= position[artist_1]
    x1, y1= position[artist_2]
    text= artist_1 + '--' + artist_2 + ': ' + str(G.edges()[edge]['weight'])
    trace= make_edge([x0, x1, None], [y0, y1, None], text, 
                       width = 0.3*G.edges()[edge]['weight']**1.5)

    edge_trace.append(trace)


#Customize layout
layout= go.Layout(
    paper_bgcolor='rgba(0,0,0,0)', # transparent background
    plot_bgcolor='rgba(0,0,0,0)', # transparent 2nd background
    xaxis =  {'showgrid': False, 'zeroline': False}, # no gridlines
    yaxis = {'showgrid': False, 'zeroline': False}, # no gridlines
)

# Create figure
fig= go.Figure(layout= layout)

# Add all edge traces, and add node trace
for trace in edge_trace:
    fig.add_trace(trace)

fig.add_trace(node_trace)

fig.update_layout(showlegend = False)# Remove legend
fig.update_xaxes(showticklabels = False)# Remove tick labels
fig.update_yaxes(showticklabels = False)# Show figure
fig.show()