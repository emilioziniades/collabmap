import pickle
import json
from pprint import pprint

import collabmap

#AUTHENTICATION

current_token = collabmap.get_auth_token()
token_header = {'Authorization':f'Bearer {current_token}'}

#SEARCH FOR ARTIST

search_prompt = 'Dope Saint Jude'
main_artist = collabmap.search(search_prompt, token_header)

#RECURSIVELY CREATE COLLAB DICT UP TO SPECIFIED DEPTH

collab_dict = {main_artist:{}}
collab_dict = collabmap.make_collab_dict(collab_dict, 3, token_header)

pprint(collab_dict)

#SAVE TO FILE 

with open('collab.pickle', 'wb') as f:
    pickle.dump(collab_dict, f)

'''
TODO



'''