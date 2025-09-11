#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
always_one.py
-------------
Example Expanding Nim client that always plays the move:
    - Take 1 stone
    - Never use a reset

This file shows how to connect to the Expanding Nim manager and automatically
make moves without human input. You can run it in place of ./exp-nim.
"""

import atexit
import sys
from client import Client   # This is provided in your repo


def check_game_status(game_state):
    """
    Helper function:
    - The manager tells us if the game is finished by setting 'finished': True
    - If so, print the reason (who won / why) and exit immediately
    """
    if game_state['finished']:
        print(game_state['reason'])
        sys.exit(0)


def my_algo(_game_state):
    """
    Strategy function:
    - In a real bot, you'd use the game_state to decide the best move.
    - Here we ignore game_state entirely and always return (1, False):
        * 1 stone taken
        * False means "do not use a reset"
    """
    return 1, False


if __name__ == "__main__":
    # ---------------------------
    # Step 1: Parse command-line arguments
    # ---------------------------
    # We want a similar interface to ./exp-nim, e.g.:
    #   python always_one.py -f -n Bob localhost:9000
    #
    # Arguments:
    #   -n NAME         -> player's name
    #   -f              -> goes first
    #   host:port       -> where the manager is running
    #
    if len(sys.argv) < 4:
        print("Usage: python always_one.py -n NAME host:port [-f]")
        sys.exit(1)

    goes_first = False
    name = None
    host, port = None, None

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "-n":
            # Player name follows -n
            name = args[i+1]
        elif arg == "-f":
            # -f flag means "this player goes first"
            goes_first = True
        elif ":" in arg:
            # Host and port provided like localhost:9000
            host, port = arg.split(":")
            port = int(port)

    if not name or not host or not port:
        print("Error: missing required arguments")
        sys.exit(1)

    # ---------------------------
    # Step 2: Connect to the server
    # ---------------------------
    client = Client(name, goes_first, (host, port))

    # Make sure we close the connection cleanly when the program exits
    atexit.register(client.close)

    print(f"Connected as {name}.")
    print(f"Game has {client.init_stones} stones, {client.init_resets} resets, and {client.game_time}.")

    # ---------------------------
    # Step 3: If this bot goes first, make an initial move
    # ---------------------------
    if goes_first:
        num_stones, reset = my_algo(None)   # We don’t have a state yet
        print(f"{name} takes {num_stones} stones (first move)")
        check_game_status(client.make_move(num_stones, reset))

    # ---------------------------
    # Step 4: Main game loop
    # ---------------------------
    # Repeatedly:
    #   - Wait for opponent's move from the server
    #   - Check if the game ended
    #   - Choose our move using my_algo()
    #   - Send the move to the server
    #
    while True:
        # Wait for the server to send the latest game state
        game_state = client.receive_move()
        check_game_status(game_state)

        # Decide what to do (always 1 stone, no reset)
        num_stones, reset = my_algo(game_state)
        print(f"{name} takes {num_stones} stones")
        check_game_status(client.make_move(num_stones, reset))