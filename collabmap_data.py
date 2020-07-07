import pickle
from pprint import pprint

import collabmap

#AUTHENTICATION

current_token = collabmap.get_auth_token()
token_header = {'Authorization':f'Bearer {current_token}'}

#SEARCH FOR ARTIST

search_prompt = 'Dope Saint Jude'
main_artist = collabmap.search(search_prompt, token_header)

#FIRST LAYER OF COLLABORATIONS

print('Now counting collaborations for {}'.format(main_artist.name))
collab_dict = collabmap.make_collab_dict(main_artist, headers=token_header)
collab_dict = {main_artist:dict(collab_dict)}

#SECOND LAYER OF COLLABORATIONS

for artist, collaborators in collab_dict.items():

    for artist1, collaborators1 in collaborators.items():

        print(f'\nNow counting collaborations for {artist1.name} w/link: {artist1.link}')
        current_collab_dict = collabmap.make_collab_dict(artist1, headers=token_header)

        collab_dict[artist][artist1] = current_collab_dict

pprint(collab_dict)

# for k,v in collab_dict.items():
#     print(k,v)
#     for k1, k2 in v.items():
#         print(k1, k1.parent_collab_count)


#SAVE TO FILE 

with open('collab.pickle', 'wb') as f:
    pickle.dump(collab_dict, f)


######


'''
TODO



'''