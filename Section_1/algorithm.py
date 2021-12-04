import sys

from world import log, world, HELLO_MSG

got_hello_from = []


def process_msg(src, msg):
    log(f"message from {src}: {msg}")

    if msg == "exit":
        sys.exit()
    elif msg == HELLO_MSG:
        got_hello_from.append(src)

    if set(got_hello_from) == set(world.neighbors):
        world.send_message(to=world.current_node, msg='exit')  # TODO Maybe you want start your algorithm here!
