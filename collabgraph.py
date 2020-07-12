import plotly.graph_objects as go
import networkx as nx


class CollabGraph():

    def __init__(self):

        self.layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            showlegend=False
            )


    def make_node_trace(self, graph, position):

        node_trace = go.Scatter(x=[],
                                y=[],
                                text=[],
                                textposition="top center",
                                textfont_size=[],
                                mode='markers+text',
                                hoverinfo='none',
                                marker=dict(color=[],
                                            size=[],
                                            line=None))

        # For each node, get the position and size and add to the node_trace
        for node in graph.nodes():

            x, y = position[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['textfont_size'] += tuple([2*graph.nodes[node]['size']])
            node_trace['marker']['color'] += tuple(['cornflowerblue'])
            node_trace['marker']['size'] += tuple([3*graph.nodes[node]['size']])
            node_trace['text'] += tuple(['<b>' + node + '</b>'])

        return node_trace


    def make_edge_traces(self, graph, position):
        '''
        For each edge, make an edge_trace, append to list

        Input: graph object, position object
        Output: list of edge traces

        Functions used: _make_edge
        '''
        edge_traces = []
        for edge in graph.edges():

            artist_1 = edge[0]
            artist_2 = edge[1]
            x0, y0 = position[artist_1]
            x1, y1 = position[artist_2]
            text = artist_1 + '--' + artist_2 + ': ' + str(graph.edges()[edge]['weight'])

            trace = self._make_edge([x0, x1, None],
                                    [y0, y1, None],
                                    text,
                                    width=0.3*graph.edges()[edge]['weight']**1.1)

            edge_traces.append(trace)

        return edge_traces


    def _make_edge(self, x, y, text, width):
        '''
        Custom function to create an edge between node x and node y, with a given text and width
        '''
        return go.Scatter(x=x,
                          y=y,
                          line=dict(width=width,
                                    color='cornflowerblue'),
                          hoverinfo='text',
                          text=([text]),
                          mode='lines')

    def add_nodes_and_edges_traces(self, node_trace, edge_traces, figure):

        figure.add_trace(node_trace)
        for edge_trace in edge_traces:
            figure.add_trace(edge_trace)


def make_nodes(collab_dict, graph):

    for artist, collaborators in collab_dict.items():

        graph.add_node(artist.name)
        make_nodes(collaborators, graph)


def make_edges(collab_dict, graph):

    for artist, collaborators in collab_dict.items():
        for artist1, collaborators1 in collaborators.items():

            graph.add_edge(artist.name, artist1.name, weight= artist1.parent_collab_count)
            make_edges(collaborators, graph)


def resize_nodes(graph, center, scale=5):

    for node in graph.nodes():

        current_distance = nx.shortest_path_length(graph, center, node)
        current_size = 1/(current_distance+ 1)*14

        graph.nodes[node]['size'] = current_size






''' 
TODO 

Structural issues

    - refactor code so that all collab_dict functions are within a CDict clas
    - Find way to avoid passing headers through every function (globals?)

Code efficiency

    - double counting albums?

Language processing

    - catch errors like 'mavi' and "MAVI" being two different artists


'''    
