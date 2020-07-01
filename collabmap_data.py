import json
from collections import defaultdict
from pprint import pprint

import requests

import collabmap

#AUTHENTICATION

current_token = collabmap.get_auth_token()
token_header = {'Authorization':f'Bearer {current_token}'}

#SEARCH FOR ARTIST

search_phrase= 'Dope Saint Jude'

payload= {'q': search_phrase, 'type': 'artist'}
search_url= 'https://api.spotify.com/v1/search'
search = requests.get(search_url, headers=token_header, params=payload)
search_data = search.json()

first_result = search_data['artists']['items'][0]
artist_name = first_result['name']
artist_link = '{}/albums'.format(first_result['href'])

#MAKE DICTIONARY OF COLLABORATIONS WITH MAIN ARTIST

print(f'Now counting collaborations for {artist_name}')
collab_dict, link_dict = collabmap.make_collab_dict(artist_link, artist_name= artist_name
                                    , headers=token_header)

#SECOND LAYER OF COLLABORATIONS

for artist, link in link_dict.items():

    print(f'\nNow counting collaborations for {artist}')
    current_collab_dict, current_link_dict = collabmap.make_collab_dict(link, artist_name= artist, headers=token_header)
    
    collab_dict.update(current_collab_dict)

with open('test.json', 'w') as f:
    json.dump(collab_dict, f, indent=4)


'''
TODO

-Handle pagination with lots of results (check 'next' in API result)
-Search queries (search_url = 'https://api.spotify.com/v1/search')

'''