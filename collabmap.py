import json
from datetime import datetime
from collections import defaultdict
from pprint import pprint

import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import plotly.graph_objects as go


class CollabGraph():

    def __init__(self):

        self.layout= go.Layout(
            paper_bgcolor='rgba(0,0,0,0)', # transparent background
            plot_bgcolor='rgba(0,0,0,0)', # transparent 2nd background
            xaxis =  {'showgrid': False, 'zeroline': False, 'showticklabels': False}, # no gridlines
            yaxis = {'showgrid': False, 'zeroline': False, 'showticklabels': False}, # no gridlines
            showlegend = False
    )


    def make_node_trace(self, graph, position):

        node_trace = go.Scatter(x         = [],
                            y         = [],
                            text      = [],
                            textposition = "top center",
                            textfont_size = [],
                            mode      = 'markers+text',
                            hoverinfo = 'none',
                            marker    = dict(color = [],
                                             size  = [],
                                             line  = None))

        # For each node, get the position and size and add to the node_trace
        for node in graph.nodes():
            x, y = position[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['textfont_size'] += tuple([2*graph.nodes[node]['size']])
            node_trace['marker']['color'] += tuple(['cornflowerblue'])
            node_trace['marker']['size'] += tuple([5*graph.nodes[node]['size']])
            node_trace['text'] += tuple(['<b>' + node + '</b>'])

        return node_trace


    def make_edge_traces(self, graph, position):
        '''
        For each edge, make an edge_trace, append to list

        Input: graph object, position object
        Output: list of edge traces

        Functions used: _make_edge
        '''
        edge_traces = []
        for edge in graph.edges():
            
            artist_1= edge[0]
            artist_2= edge[1]
            x0, y0= position[artist_1]
            x1, y1= position[artist_2]
            text= artist_1 + '--' + artist_2 + ': ' + str(graph.edges()[edge]['weight'])
            
            trace= self._make_edge([x0, x1, None], [y0, y1, None], text, 
                               width = 0.3*graph.edges()[edge]['weight']**1.1)

            edge_traces.append(trace)

        return edge_traces


    def _make_edge(self, x, y, text, width):
        '''
        Custom function to create an edge between node x and node y, with a given text and width
        '''
        return  go.Scatter(x         = x,
                           y         = y,
                           line      = dict(width = width,
                                            color = 'cornflowerblue'),
                           hoverinfo = 'text',
                           text      = ([text]),
                           mode      = 'lines')


def cacheToken(decorated):
    '''
    Decorator that checks authorization token and refreshes if necessary
    '''
    def wrapper():

        with open('auth_token.json', 'r') as f:
            token_data = json.load(f)

        token_expiry = datetime.fromtimestamp(token_data['expires_at'])
        now = datetime.now()

        token_expired = (token_expiry < now)
        
        if token_expired:
            #Get new token and update auth_token.json
            print('Token has expired. Getting new token \n')
            return decorated()
        else:
            #Use existing token
            print('Using cached token \n')
            return token_data['access_token']

    return wrapper


@cacheToken
def get_auth_token():
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
    artist_link_dict = {}


    for album_name, album_link in current_album_dict.items():

        print(f'Now counting collaborations from {album_name}')

        current_link = album_link + '/tracks'
        _count_collaborations(current_link, collab_defaultdict, artist_link_dict, main_artist=artist_name, headers=headers)

    collab_dict = {}
    collab_dict[artist_name] = dict(collab_defaultdict)

    return collab_dict, artist_link_dict


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


def _count_collaborations(album_url, collab_dict, link_dict, main_artist, headers):
    '''
    For a given album, function adds to pre-existing collaboration dictionary
    '''
    payload  = {'limit':'50'}

    r = requests.get(album_url, headers=headers, params=payload)

    tracks = r.json()['items']

    for track in tracks:
        
        #Generates dict of artists featured on track and their link
        current_artists = {}
        for artist in track['artists']:
            artist_i = artist['name']
            artist_i_link = artist['href']
            current_artists[artist_i] = artist_i_link

        #If main artist featured, count the others on that song and add to link dict
        if main_artist in current_artists:
            del current_artists[main_artist]

            #Count the collaboration
            for current_artist in current_artists.keys():
                collab_dict[current_artist] += 1

            #Add link to link_dict
            for current_artist, current_artist_link in current_artists.items():
                link_dict[current_artist] = current_artist_link + '/albums'



'''
TODO 

Refactor code heectic!

'''    
