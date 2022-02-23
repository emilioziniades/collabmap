'''
Module containing CollabGraph to generate network and associated visualization
'''
import plotly.graph_objects as go
import networkx as nx


class CollabNetwork(nx.Graph):
    
    def __init__(self, collab_dict):

        nx.Graph.__init__(self)

        self.collab_dict = collab_dict
        self._generate_network(self.collab_dict)

    def _generate_network(self, collab_dict):

        #POPULATE GRAPH WITH NODES AND EDGES

        #Add nodes and edges recursively
        self._make_nodes(collab_dict)
        self._make_edges(collab_dict)

        #Resize nodes
        main_artist = list(collab_dict.keys())[0].name
        self._resize_nodes(main_artist)


    def _make_nodes(self, collab_dict):

        for artist, collaborators in collab_dict.items():
            self.add_node(artist.name)
            self._make_nodes(collaborators)


    def _make_edges(self, collab_dict):

        for artist, collaborators in collab_dict.items():
            for artist1, collaborators1 in collaborators.items():

                self.add_edge(artist.name, artist1.name, weight=artist1.parent_collab_count)
                self._make_edges(collaborators)


    def _resize_nodes(self, center, scale=5):

        for node in self.nodes():

            current_distance = nx.shortest_path_length(self, center, node)
            current_size = 1/(current_distance + 1)*14

            self.nodes[node]['size'] = current_size


    def position_network(self, parameters):

        #Position graphs and edges
        return nx.spring_layout(self, 
                                scale=None,
                                k=parameters['k'],
                                iterations=parameters['iterations'])


class CollabGraph(go.Figure):

    def __init__(self):

        go.Figure.__init__(self)

        self.layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            showlegend=False
            )


    def draw_graph(self, network, position, save=False, filename=None):

        # Create node traces, edge traces and add to figure
        node_trace = self._make_node_trace(network, position)
        edge_traces = self._make_edge_traces(network, position)

        # Add node trace and add all edge traces
        self._add_nodes_and_edges_trace(node_trace, edge_traces)

        #TO SEE
        self.show()

        if save:

            # k = parameters['k']
            # filename = f'graph_k_{k}'
            self.write_image(f'graphs/{filename}.png')


    def _make_node_trace(self, graph, position):

        node_trace = go.Scatter(x=[],
                                y=[],
                                text=[],
                                textposition="top center",
                                textfont_size=[],
                                mode='markers+text',
                                hoverinfo='none',
                                marker=dict(color=[],
                                            size=[],
                                            opacity=[],
                                            line=None))

        # For each node, get the position and size and add to the node_trace
        for node in graph.nodes():

            x, y = position[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['textfont_size'] += tuple([2*graph.nodes[node]['size']])

            marker_size=3*graph.nodes[node]['size']
            marker_opacity= 1- (1/marker_size)

            node_trace['marker']['color'] += tuple(['cornflowerblue'])
            node_trace['marker']['size'] += tuple([marker_size])
            node_trace['marker']['opacity'] += tuple([marker_opacity])
            
            node_trace['text'] += tuple(['<b>' + node + '</b>'])

        return node_trace


    def _make_edge_traces(self, graph, position):
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


    def _add_nodes_and_edges_trace(self, node_trace, edge_traces):

        self.add_trace(node_trace)
        for edge_trace in edge_traces:
            self.add_trace(edge_trace)

    
''' 
TODO 

-Opacity is off


'''    
