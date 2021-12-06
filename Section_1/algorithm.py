import sys

from world import log, world, HELLO_MSG

SEPARATOR = '#'

got_msg_from = []
parent = []
subtree_size = []


def echo_extinction(src, msg):
    splited_msg = msg.split(SEPARATOR)
    if int(splited_msg[1]) > int(world.current_leader_round) or (int(splited_msg[1]) == int(world.current_leader_round)
                                                                 and int(splited_msg[2]) > int(world.current_leader_id)):
        # if len(parent) != 0:
        #     parent.pop()
        parent.clear()
        got_msg_from.clear()
        subtree_size.clear()

        parent.append(src)
        world.current_leader_round = splited_msg[1]
        world.current_leader_id = splited_msg[2]
        got_msg_from.append(src)
        for n in world.neighbors:
            if n != src:
                world.send_message(to=n, msg=msg)

    if int(splited_msg[1]) < int(world.current_leader_round) or (int(splited_msg[1]) == int(world.current_leader_round)
                                                                 and int(splited_msg[2]) > int(world.current_leader_id)):
        return

    if int(splited_msg[1]) == int(world.current_leader_round) and int(splited_msg[2]) == int(world.current_leader_id):
        subtree_size.append(int(splited_msg[3]))
        got_msg_from.append(src)


def process_msg(src, msg):
    log(f"message from {src}: {msg}")
    if msg == "exit":
        print(f'## algorithm terminated:\n after round {world.current_leader_round} : parent is {parent} and leader id is {world.current_leader_id}')
        for n in world.neighbors:
            if n != world.current_node:
                world.send_message(n, msg)
        sys.exit()
    else:
        if src != world.current_node:
            echo_extinction(src, msg)
        else:
            got_msg_from.append(src)

    if set(got_msg_from) == set(world.neighbors):
        log(f'after round {world.current_leader_round} : parent is {parent} and leader id is {world.current_leader_id}')

        if len(parent) != 0:
            world.send_message(to=parent[0], msg="wave" + "#" + world.current_leader_round + "#" +
                                                 world.current_leader_id + "#" + str(sum(subtree_size) + 1))
        else:
            if (int(msg.split(SEPARATOR)[3]) + 1) == world.number_of_nodes_world_map:
                print(f'### I am the leader after round {world.current_leader_round} and my id is {world.current_leader_id}')
                for n in world.neighbors:
                    if n != world.current_node:
                        world.send_message(to=n, msg='exit')
                sys.exit()
            else:
                world.start_round(str(int(world.current_leader_round) + 1))
