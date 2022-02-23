'''
Driver code for collecting data from Spotify API and storing it in a collab_dict

'''
import pickle
from pprint import pprint

import requests_cache

import collabdict

#Cache set on 14 July 2020
requests_cache.install_cache('collabcache')

#AUTHENTICATION

current_token = collabdict.get_auth_token()
token_header = {'Authorization':f'Bearer {current_token}'}

#SEARCH FOR ARTIST

search_prompt = 'Kanye West'
main_artist = collabdict.search(search_prompt, token_header)
print(main_artist)

#RECURSIVELY CREATE COLLAB DICT UP TO SPECIFIED DEPTH

collab_dict = collabdict.CollabDict(main_artist, token_header, depth=3)


# pprint(collab_dict)
###

'''
Catch naming errors example with Medhane, depth=3

case-difference:
    without: 454 artists
    with:    448 artists
'''


###

#SAVE TO FILE 

with open('collab.pickle', 'wb') as f:
    pickle.dump(collab_dict, f)

'''
TODO

---
Kanye West, Earl Sweatshirt, Medhane, Dope Saint Jude


'''