import json
from datetime import datetime
from collections import defaultdict
from pprint import pprint

import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class Decorators():

    @staticmethod
    def refreshToken(decorated):
        '''
        Checks authorization token and refreshes if necessary

        TODO: USE THIS TO DECORATE get_auth_token
        '''
        pass


def get_auth_token():

    with open('auth_token.json', 'r') as f:
        token_data = json.load(f)
  
    def _token_expired():
        '''
        Returns a boolean indicating whether access token has expired
        '''
        token_expiry = datetime.fromtimestamp(token_data['expires_at'])
        now = datetime.now()

        return token_expiry < now

    def _get_new_token():
        '''
        Obtains fresh authorization token from Spotify API via Client Credential
        Flow and stores token and expiry time as JSON
        '''
        CLIENT_ID = '5877586bdfe74c348ef767443058061c'
        CLIENT_SECRET = '59fcea665e9443059576f1eaf324e47d'
        AUTH_URL = 'https://accounts.spotify.com/api/token'

        client = BackendApplicationClient(client_id=CLIENT_ID)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=AUTH_URL, client_id=CLIENT_ID, 
                            client_secret=CLIENT_SECRET)

        token_dict = {'access_token': token['access_token'],
                            'expires_at': token['expires_at']}

        with open('auth_token.json', 'w') as f:
            json.dump(token_dict, f)

        return token['access_token']

    if _token_expired():
        #Get new token and update auth_token.json
        print('Token has expired. Getting new token \n')
        return _get_new_token()
    else:
        #Use existing token
        print('Using cached token \n')
        return token_data['access_token']


def _make_album_dict(artist_url, headers, payload):
    '''
    Input: Artist URL, auth token headers and payload
    Output: Dictionary of the form {album name: album url
    '''

    r = requests.get(artist_url, headers=headers, params=payload)
    current_data = r.json()

    current_album_dict = {}
    for item in current_data['items']:
        album = item['name']
        album_link = item['href']

        current_album_dict[album] = album_link

    print(f'NUMBER OF ALBUMS TO COUNT: {len(current_album_dict)}')

    return current_album_dict


def _count_collaborations(album_url, current_dict, main_artist, headers):
    '''
    For a given album, function adds to pre-existing collaboration dictionary
    '''
    payload  = {'limit':'50'}

    r = requests.get(album_url, headers=headers, params=payload)

    tracks = r.json()['items']

    for track in tracks:
        
        #Generates list of artists featured on track
        current_artists = []
        for artist in track['artists']:
            artist_i = artist['name']
            current_artists.append(artist_i)

        #If main artist featured, count the others on that song
        if main_artist in current_artists:
            current_artists.remove(main_artist)

            for current_artist in current_artists:
                current_dict[current_artist] += 1


def make_collab_dict(artist_url, headers, artist_name):
    '''
    Input: root artist url, auth token in header
    Output: Default dict of the form {collaborator: collaboration count}

    Functions used: _make_album_dict, _count_collaborations
    '''
    #Make list of all albums from one artist 
    payload = {'limit':'50',
                'include_groups':'album,single,appears_on'}
    current_album_dict = _make_album_dict(artist_url, headers=headers, payload=payload)

    #Get all collaborations from each album on list

    collab_defaultdict = defaultdict(lambda: 0)
    for album_name, album_link in current_album_dict.items():

        print(f'Now counting collaborations from {album_name}')

        current_link = album_link + '/tracks'
        _count_collaborations(current_link, collab_defaultdict, main_artist=artist_name, headers=headers)

    collab_dict = {}
    collab_dict[artist_name] = dict(collab_defaultdict)

    return collab_dict

'''
TODO 

-Decorate get_auth_token
'''    
