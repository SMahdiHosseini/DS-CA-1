import sys

from world import log, world, HELLO_MSG

SEPARATOR = '#'

got_vote_from = []
got_ack_from = [world.current_node]


def handle_change_message(src, votes_num):
    if votes_num > world.votes:
        world.send_message(src, "ACK")
    elif votes_num == world.votes and int(src) > int(world.current_node):
        world.send_message(src, "ACK")
    else:
        log(f'I am have better chance of being a leader!')


def handle_crq_message(src):
    if world.voted:
        log(f'I have voted before!')
        world.send_message(src, "vote#0")
    else:
        if src == world.current_node:
            world.set_voted(True)
            log('I vote myself')
            world.send_message(world.current_node, "vote#1")
        else:
            if world.is_active:
                world.send_message(src, "vote#0")
            else:
                world.set_voted(True)
                world.send_message(src, "vote#1")


def process_msg(src, msg):
    log(f"message from {src}: {msg}")
    splited_msg = msg.split(SEPARATOR)

    if splited_msg[0] == "CRQ":
        world.add_message()
        handle_crq_message(src)

    if splited_msg[0] == "vote":
        world.add_vote(int(splited_msg[1]))
        got_vote_from.append(src)
        if set(got_vote_from) == set(world.all_nodes()):
            for n in world.active_sources:
                if n != world.current_node:
                    world.send_message(n, f'CHANGE#{world.votes}')
            if len(world.active_sources) == 1:
                world.send_message(world.current_node, f'ACK')

    if splited_msg[0] == "CHANGE":
        handle_change_message(src, int(splited_msg[1]))

    if splited_msg[0] == "ACK":
        got_ack_from.append(src)
        if set(got_ack_from) == set(world.active_sources):
            for n in world.all_nodes():
                world.send_message(n, f'CAM#{world.current_node}')

    if splited_msg[0] == "CAM":
        world.add_message()
        log(f'third phase started!')
        print(f'## algorithm terminated and leader id is {src}')
        print(f'** number of messages = {world.number_of_messages}')
        sys.exit()
