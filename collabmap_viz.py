import json

import pygraphviz as pgv

with open('test.json', 'r') as f:
    test_dict = json.load(f)

main_artist = list(test_dict.keys())[0]
collaborators = list(test_dict['Medhane'].keys())



G = pgv.AGraph(directed=False)
G.add_node(main_artist)
G.add_nodes_from(collaborators)

for collaborator in collaborators:
    G.add_edge(main_artist, collaborator)

G.layout(prog='neato')

G.draw('testiiin.png')

