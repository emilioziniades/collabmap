import json
from datetime import datetime

import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import plotly.graph_objects as go

class Artist:

    def __init__(self, name, link):

        self.name = name
        self.link = link
        self.parent_collab_count = 1

    def __str__(self):

        return f'{self.name}'


class CollabGraph:

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


class Decorators:

    @staticmethod
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


@Decorators.cacheToken
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


def search(artist_name, token_header):

    payload= {'q': artist_name, 'type': 'artist'}
    search_url= 'https://api.spotify.com/v1/search'
    search = requests.get(search_url, headers=token_header, params=payload)
    search_data = search.json()

    first_result = search_data['artists']['items'][0]
    artist_name = first_result['name']
    artist_link = '{}/albums'.format(first_result['href'])

    main_artist_object = Artist(artist_name,artist_link )

    return main_artist_object


def make_collab_dict(artist_obj, headers):
    '''
    Input: artist (Artist object), auth token in header
    Output: Default dict of the form {collaborator: collaboration count}

    Functions used: _make_album_dict, _count_collaborations
    '''

    #Make list of all albums from one artist 
    payload = {'limit':'50',
                'include_groups':'album,single,appears_on'}
    album_dict = _make_album_dict(artist_obj.link, headers=headers, payload=payload)

    #Get all collaborations from each album on list

    collab_dict = {}

    for album_name, album_link in album_dict.items():

        print(f'Now counting collaborations from {album_name}')
        _count_collaborations(album_link, collab_dict, main_artist=artist_obj.name, headers=headers)

    return collab_dict


def _make_album_dict(artist_url, headers, payload):
    '''
    Input: Artist URL, auth token headers and payload
    Output: Dictionary of the form {album name: album url
    '''
    album_dict = {}
    current_data = requests.get(artist_url, headers=headers, params=payload).json()

    page_count = 1
    while True:

        #Adding results on current page
        for item in current_data['items']:
            album = item['name']
            album_link = item['href'] + '/tracks'
            album_dict[album] = album_link

        #Check for next page and make new request for that data
        if current_data['next']:
            next_url = current_data['next']
            next_r = requests.get(next_url, headers=headers, params=payload)
            current_data = next_r.json()
            page_count += 1
        else:
            break

    print(f'NUMBER OF ALBUMS TO COUNT: {len(album_dict)} from {page_count} page(s)')
    return album_dict


def _count_collaborations(album_url, collab_dict, main_artist, headers):
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
            artist_i_link = artist['href'] + '/albums'
            current_artists[artist_i] = artist_i_link

        #If main artist featured, count the others on that song and add to link dict
        if main_artist in current_artists:
            del current_artists[main_artist]

            #Count the collaboration and add link to collab_dict
            for current_artist, current_artist_link in current_artists.items():

                #if artist already in dictionary: increment its associated value
                for artist in collab_dict.keys():

                    if current_artist == artist.name:
                        print('We found the artist already!')
                        artist.parent_collab_count += 1
                        break

                else:
                #else create new artist object and add to collab dict
                    current_artist_object = Artist(name= current_artist, link= current_artist_link)
                    collab_dict[current_artist_object] = {}


def recursive_collab_dict(collab_dict, headers, depth=3):

    count= 1
    for k,v in collab_dict.items():

        if count < depth:
            print(f'Counting collaborations for: {k}')
            current_collab_dict = make_collab_dict(v, headers=headers)
            collab_dict[k] = current_collab_dict
            #current_collab_dict = make_collab_dict
            #update existing dict
            recursive_collab_dict(v)
        else:            
            break
        count += 1
''' 
TODO 

-Consider restructuring data storage so that collab_dict and link_dict are a single item
    -Idea: have an artist class that includes their name and link?


'''    
