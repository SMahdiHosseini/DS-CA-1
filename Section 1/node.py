#! /usr/bin/python3

import sys

from world import world, log

if __name__ == '__main__':
    log(f'Hello from node{world.current_node}')
    log(f'I\'m connected to nodes {world.neighbors}')
    log(f'I have edges {world.edges}')

    world.send_hello()
    try:
        world.listen()
    except KeyboardInterrupt:
        log("received keyboard interrupt")
        sys.exit(0)
