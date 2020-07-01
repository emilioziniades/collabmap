import json
from collections import defaultdict
from pprint import pprint

import requests

import collabmap

current_token = collabmap.get_auth_token()
headers = {'Authorization':f'Bearer {current_token}'}

#DOPE ST JUDE EXAMPLE 

dsj_url = 'https://api.spotify.com/v1/artists/6lTiYE2IL4FUqf0CgGjI5i/albums'
dsj_dict = collabmap.make_collab_dict(dsj_url, artist_name='Medhane'
                                    , headers=headers)

with open('test.json', 'w') as f:
    json.dump(dsj_dict, f, indent=4)

print('\n')
pprint(dsj_dict)


'''
TODO

-Handle pagination with lots of results (check 'next' in API result)
-Search queries (search_url = 'https://api.spotify.com/v1/search')

'''