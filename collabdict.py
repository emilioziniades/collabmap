"""
Module containing Artist class, self class, as well as other API related
functions
"""
import json
from datetime import datetime
import os

from dotenv import load_dotenv
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class Artist:
    """
    Artist object to be contained in self nested dictionary
    """

    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.parent_collab_count = 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name


class CollabDict(dict):
    """
    Dictionary subclass which contains nested dictionaries of artist objects
    """

    def __init__(self, main_artist="NONE", headers="FAIL", depth=1):

        dict.__init__(self)
        self.update({main_artist: {}})
        self.make_collab_dict(headers, depth)

    def make_collab_dict(self, headers, depth):
        """
        Function that makes a collab_dict of a specified depth recursively

        Input: dictionary with main artist, depth, authentication headers

        Output: Nested collab dictionary

        Functions used: _count_artist_collabs
        """
        visited = []

        def rec_collab_dict(self, headers, depth, visited, count=1):

            if count < depth:

                for artist, collaborators in self.items():

                    if artist.name not in visited:
                        print(
                            "\nNow counting collaborations for {}".format(artist.name)
                        )
                        current_collab_dict = CollabDict._count_artist_collabs(
                            artist_obj=artist, headers=headers
                        )
                        collaborators.update(current_collab_dict)
                        visited.append(artist.name)
                    else:
                        print(
                            f"\nSkipping {artist.name} because they have been counted"
                        )

                    rec_collab_dict(collaborators, headers, depth, visited, count + 1)

            return self

        return rec_collab_dict(self, headers, depth, visited)

    def artist_list(self):

        output = {}

        def rec_flatten(self, output):

            for k, v in self.items():

                current_list = []

                for x in v.keys():
                    current_list.append(x)

                output[k] = current_list

                rec_flatten(v, output)

        rec_flatten(self, output)

        return list(output.keys())

    @staticmethod
    def _count_artist_collabs(artist_obj, headers):
        """
        Input: artist (Artist object), auth token in header
        Output: Default dict of the form {collaborator: collaboration count}

        Functions used: _make_album_dict, _count_album_collaborations
        """

        # Make list of all albums from one artist
        album_dict = CollabDict._make_album_dict(artist_obj.link, headers)

        # Get all collaborations from each album on list
        collab_dict = {}

        for album_link in album_dict.values():

            CollabDict._count_album_collaborations(
                album_link, collab_dict, artist_obj.name, headers
            )

        return collab_dict

    @staticmethod
    def _make_album_dict(artist_url, headers):
        """
        Input: Artist URL, auth token headers and payload
        Output: Dictionary of the form {album name: album url
        """

        album_dict = {}
        payload = {"limit": "50", "include_groups": "album,single,appears_on"}

        current_data = requests.get(artist_url, headers=headers, params=payload).json()

        page_count = 1
        while True:

            # Adding results on current page
            for item in current_data["items"]:
                album = item["name"]
                album_link = item["href"] + "/tracks"
                album_dict[album] = album_link

            # Check for next page and make new request for that data
            if current_data["next"]:
                next_url = current_data["next"]
                next_r = requests.get(next_url, headers=headers, params=payload)
                current_data = next_r.json()
                page_count += 1
            else:
                break

        print(f"# of albums to count: {len(album_dict)} from {page_count} page(s)")
        return album_dict

    @staticmethod
    def _count_album_collaborations(album_url, collab_dict, main_artist, headers):
        """
        For a given album, function adds to pre-existing collaboration dictionary
        """
        payload = {"limit": "50"}
        req = requests.get(album_url, headers=headers, params=payload)

        if req.status_code != 200:
            print(f"get request failed with status code {req.status_code}")
            exit(1)

        tracks = req.json()["items"]

        for track in tracks:
            # Generates dict of artists featured on track and their link
            current_artists = {}
            for artist in track["artists"]:
                artist_i = artist["name"]
                artist_i_link = artist["href"] + "/albums"
                current_artists[artist_i] = artist_i_link

            # If main artist featured, count the others on that song and add to link dict
            if main_artist in current_artists:
                del current_artists[main_artist]

                # Count the collaboration and add link to collab_dict
                for current_artist, current_artist_link in current_artists.items():

                    # if artist already in dictionary: increment its associated value
                    for artist in collab_dict.keys():

                        if current_artist.lower() == artist.name.lower():
                            # lower() corrects for same artist with different case
                            artist.parent_collab_count += 1
                            break

                    else:
                        # else create new artist object and add to collab dict
                        current_artist_object = Artist(
                            name=current_artist, link=current_artist_link
                        )
                        collab_dict[current_artist_object] = {}


def cache_token(decorated):
    """
    Decorator that checks authorization token and refreshes if necessary
    """

    def wrapper():

        try:
            with open("data/auth_token.json", "r") as file:
                token_data = json.load(file)
        except FileNotFoundError:
            # Initialize auth_token.json file
            print("No token found. Getting token.")
            return decorated()

        token_expiry = datetime.fromtimestamp(token_data["expires_at"])

        if token_expiry < datetime.now():
            # Get new token and update auth_token.json
            print("Token has expired. Getting new token")
            return decorated()

        # Otherwise use existing token
        print("Using cached token \n")
        return token_data["access_token"]

    return wrapper


@cache_token
def get_auth_token():
    """
    Obtains fresh authorization token from Spotify API via Client Credential
    Flow and stores token and expiry time as JSON
    """

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    auth_url = "https://accounts.spotify.com/api/token"

    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url=auth_url, client_id=client_id, client_secret=client_secret
    )

    token_dict = {
        "access_token": token["access_token"],
        "expires_at": token["expires_at"],
    }

    with open("data/auth_token.json", "w") as file:
        json.dump(token_dict, file)

    return token["access_token"]


def search(artist_name, token_header):
    """
    Searches the Spotify database for an artist named 'artist_name'
    """
    payload = {"q": artist_name, "type": "artist"}
    search_url = "https://api.spotify.com/v1/search"
    search_req = requests.get(search_url, headers=token_header, params=payload)
    search_data = search_req.json()

    first_result = search_data["artists"]["items"][0]
    artist_name = first_result["name"]
    artist_link = "{}/albums".format(first_result["href"])

    main_artist_object = Artist(artist_name, artist_link)

    return main_artist_object


""" 
TODO 

Structural issues


    - Find way to avoid passing headers through every function (globals?)

Code efficiency

    - double counting albums?

Language processing

    - catch errors like 'mavi' and "MAVI" being two different artists

"""
