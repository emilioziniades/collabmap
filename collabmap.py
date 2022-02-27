"""
Driver code for collecting data from Spotify API, storing it in a collab_dict and generate graph from it

"""
import argparse
from typing import Tuple

import requests_cache

import collabdict
import collabgraph


def main():

    # CACHING

    requests_cache.install_cache("data/collabcache")

    # AUTHENTICATION

    current_token = collabdict.get_auth_token()
    token_header = {"Authorization": f"Bearer {current_token}"}

    # SEARCH SPOTIFY DATASET
    artist, depth = parse_arguments()

    main_artist = collabdict.search(artist, token_header)
    print(f"Generating collabmap for {main_artist}")
    collab_dict = collabdict.CollabDict(main_artist, token_header, depth=depth)

    # CREATE GRAPH OBJECT WITH NETWORKX
    collab_network = collabgraph.CollabNetwork(collab_dict)
    parameters = {"iterations": 100, "k": None}
    position = collab_network.position_network(parameters)

    # GRAPH WITH PLOTLY

    collab_graph = collabgraph.CollabGraph()
    collab_graph.draw_graph(collab_network, position)


def parse_arguments() -> Tuple[str, int]:
    # PARSE ARGUMENTS

    parser = argparse.ArgumentParser(
        description="Generate a map of collaborations centered on a specific artist"
    )
    parser.add_argument(
        "artist",
        metavar="artist",
        type=str,
        help="artist at center of collabmap",
    )
    parser.add_argument(
        "--depth",
        "-D",
        metavar="D",
        type=int,
        default=3,
        help="depth limit for collabmap",
    )
    args = parser.parse_args()
    return (args.artist, args.depth)


if __name__ == "__main__":
    main()
