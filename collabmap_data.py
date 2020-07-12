import pickle
from pprint import pprint

import collabdict

#AUTHENTICATION

current_token = collabdict.get_auth_token()
token_header = {'Authorization':f'Bearer {current_token}'}

#SEARCH FOR ARTIST

search_prompt = 'Medhane'
main_artist = collabdict.search(search_prompt, token_header)

#RECURSIVELY CREATE COLLAB DICT UP TO SPECIFIED DEPTH

initial_dict = {main_artist:{}}

collab_dict = collabdict.CollabDict(initial_dict)

collab_dict.make_collab_dict(3, token_header)

pprint(collab_dict)

#SAVE TO FILE 

with open('collab.pickle', 'wb') as f:
    pickle.dump(collab_dict, f)

'''
TODO



'''