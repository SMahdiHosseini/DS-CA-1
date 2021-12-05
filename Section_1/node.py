#! /usr/bin/python3

import sys

from world import world, log

if __name__ == '__main__':
    log(f'Hello from node{world.current_node}')
    log(f'I\'m connected to nodes {world.neighbors}')
    log(f'I have edges {world.edges}')

    r = 0
    # world.
    # world.send_hello()
    if world.current_node == str(1):
        world.start_round(r)
    try:
        world.listen()
    except KeyboardInterrupt:
        log("received keyboard interrupt")
        sys.exit(0)