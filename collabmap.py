"""
Driver code for collecting data from Spotify API, storing it in a collab_dict and generate graph from it

"""
import os
import argparse
from typing import Tuple

import requests_cache

import collabdict
import collabgraph


def main():

    create_data_cache()

    artist, depth, save = parse_arguments()

    # AUTHENTICATION

    current_token = collabdict.get_auth_token()
    token_header = {"Authorization": f"Bearer {current_token}"}

    # SEARCH SPOTIFY DATASET AND CREATE DICTIONARY OF COLLABORATIONS

    main_artist = collabdict.search(artist, token_header)
    print(f"Generating collabmap for {main_artist}")
    collab_dict = collabdict.CollabDict(main_artist, token_header, depth=depth)

    # CREATE GRAPH OBJECT WITH NETWORKX AND GRAPH WITH PLOTLY

    collab_network = collabgraph.CollabNetwork(collab_dict)
    parameters = {"iterations": 50, "k": 0.55}
    position = collab_network.position_network(parameters)
    collab_graph = collabgraph.CollabGraph()
    collab_graph.draw_graph(collab_network, position, save, f"{artist}-{depth}")


def parse_arguments() -> Tuple[str, int, bool]:

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
        help="depth limit for collabmap (default = 3)",
    )
    parser.add_argument(
        "--save",
        "-S",
        action="store_true",
        default=False,
        help="save graph as png to data directory (default = False)",
    )

    args = parser.parse_args()
    return (args.artist, args.depth, args.save)


def create_data_cache():
    if not os.path.exists("data"):
        os.mkdir("data")
    requests_cache.install_cache("data/collabcache")


if __name__ == "__main__":
    main()
