import json
from pprint import pprint

import requests

import collabmap

#AUTHENTICATION

current_token = collabmap.get_auth_token()
token_header = {'Authorization':f'Bearer {current_token}'}

#SEARCH FOR ARTIST

search_prompt = 'Dope Saint Jude'

artist_link, artist_name = collabmap.search(search_prompt, token_header)

#FIRST LAYER OF COLLABORATIONS

print(f'Now counting collaborations for {artist_name}')
collab_dict, link_dict = collabmap.make_collab_dict(artist_link, artist_name= artist_name
                                    , headers=token_header)

#SECOND LAYER OF COLLABORATIONS

# for artist, link in link_dict.items():

#     print(f'\nNow counting collaborations for {artist}')
#     current_collab_dict, current_link_dict = collabmap.make_collab_dict(link, artist_name= artist, headers=token_header)
    
#     collab_dict.update(current_collab_dict)

#SAVE TO FILE 

with open('test.json', 'w') as f:
    json.dump(collab_dict, f, indent=4)


'''
TODO



'''