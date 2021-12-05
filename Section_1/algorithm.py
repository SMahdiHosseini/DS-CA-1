import sys

from world import log, world, HELLO_MSG

got_msg_from = []
parent = []


def echo(src, msg):
    parent.append(src)
    got_msg_from.append(src)
    for n in world.neighbors:
        if n != src:
            world.send_message(to=n, msg=msg)


def process_msg(src, msg):
    log(f"message from {src}: {msg}")

    if msg == "exit":
        sys.exit()
    elif msg == 'done':
        got_msg_from.append(src)
    else:
        if src == world.current_node:
            got_msg_from.append(src)
        if len(parent) == 0 and src != world.current_node:
            echo(src, msg)

    if set(got_msg_from) == set(world.neighbors):
        print(f'parent: {parent}')
        if world.current_node != str(1):
            world.send_message(to=parent[0], msg='done')
        world.send_message(to=world.current_node, msg='exit')  # TODO Maybe you want start your algorithm here!