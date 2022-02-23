'''
Driver code to generate graph, using collab_dict data
'''

import pickle

import collabgraph

#GET DATA FROM collabmap_data

with open('collab.pickle', 'rb') as f:
    collab_dict = pickle.load(f)

artists = collab_dict.artist_list()
# print(artists)
print(len(artists))
print(len(set([artist.name.lower() for artist in artists])))
print('\n \n \n \n \n \n ')
print(sorted(set([artist.name.lower() for artist in artists])))
#31668 vs 14937

###
for artist in artists:
    for artist1 in artists:

        if artist.name.lower() == artist1.name.lower():

            if artist.name != artist1.name:
                print(artist,artist1)
###

#CREATE GRAPH OBJECT WITH NETWORKX
# collab_network = collabgraph.CollabNetwork(collab_dict)

# Position graph
parameters = {'iterations':100,
              'k':None}

# position = collab_network.position_network(parameters)

#GRAPH WITH PLOTLY

# collab_graph = collabgraph.CollabGraph()
# collab_graph.draw_graph(collab_network, position)




# for i in range(1, 10, 1):
#     print(i)
#     parameters['k'] = i/100


'''
TODO

-Determine best parameters for position of nodes

-Let collabgraph inherit from networkx?


'''
