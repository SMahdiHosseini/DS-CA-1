import argparse
import random
import socket
import sys

import networkx as nx
import pika
from networkx.classes.reportviews import EdgeDataView

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--network', dest='network_gml', help='The GML file for the simulated network.')
parser.add_argument('--world', dest='world_helper', help='The World helper type.', required=True)
parser.add_argument('--log-level', dest='log_level', help='The log level', default='info')
parser.add_argument('--force-node', dest='force_node')
parser.add_argument('--pika-host', dest='pika_host')
parser.add_argument('--simulate-network-parameters', dest='simulate_network_parameters', action='store_true')
parser.add_argument('--configs', dest="config", help='Configuration file for priority of processes ')
args = parser.parse_args()

SEPARATOR = "###$$###"
HELLO_MSG = 'hello'
PIKA_CON_PARAMETERS = {}


def log(msg, level='info'):
    print(f'[{level}] {msg}', file=sys.stderr)


def zero_one_random(p):
    return random.choices([0, 1], [1 - p, p]) == [1]


def id_random_selector(n):
    return random.choices([i for i in range(1, n + 1)])


def callback(ch, method, properties, body):
    src, msg = body.decode().split(SEPARATOR)
    return world.receive(src=src, msg=msg)


class AbstractWorld(object):
    SINGLETON = None
    current_node = None

    @property
    def name(self):
        raise NotImplementedError

    @classmethod
    def __inheritors__(cls):
        subclasses = set()
        work = [cls]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses

    @staticmethod
    def get_instance():
        if AbstractWorld.SINGLETON is None:
            try:
                AbstractWorld.SINGLETON = {cls.name: cls for cls in AbstractWorld.__inheritors__()}.get(
                    args.world_helper)()
            except TypeError:
                raise Exception('Not a valid world helper.')

        return AbstractWorld.SINGLETON

    def send_message(self, to, msg):
        raise NotImplementedError

    def listen(self):
        raise NotImplementedError

    def receive(self, src, msg):
        raise NotImplementedError

    def start_first_phase(self):
        raise NotImplementedError

    def set_voted(self, status):
        raise NotImplementedError

    @property
    def neighbors(self) -> list:
        raise NotImplementedError

    @property
    def edges(self) -> EdgeDataView:
        raise NotImplementedError

    def get_edge_data(self, u, v):
        raise NotImplementedError

    def add_message(self):
        raise NotImplementedError

    def all_nodes(self):
        raise NotImplementedError

    def start_second_phase(self):
        raise NotImplementedError

    def find_priority_from_config_file(self):
        raise NotImplementedError

    def find_active_sources(self):
        raise NotImplementedError

class SimulatorFullView(AbstractWorld):
    name = 'simulator-full-view'

    def receive(self, src, msg):
        from algorithm import process_msg
        return process_msg(src, msg)

    @staticmethod
    def pika_host(node):
        if args.pika_host is None:
            return f'node{node}'
        else:
            return args.pika_host

    def add_message(self):
        self.number_of_messages += 1

    def all_nodes(self):
        return self._world_map.nodes

    def set_voted(self, status):
        self.voted = status

    def add_vote(self, vote):
        self.votes += vote

    def listen(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.pika_host(self.current_node), **PIKA_CON_PARAMETERS)
        )
        channel = connection.channel()
        channel.queue_declare(queue=f'node{self.current_node}')
        channel.basic_consume(queue=f'node{self.current_node}',
                              auto_ack=True,
                              on_message_callback=callback)
        channel.start_consuming()

    def send_message(self, to, msg):
        log(f'send message to {to}: {msg}')
        if args.simulate_network_parameters:
            packet_loss = self.get_edge_data(self.current_node, to, key='packet_loss', default=0.0)
            if packet_loss != 0.0 and zero_one_random(packet_loss) is True:
                log(f'packet "{to}: {msg}" lost!')
                return  # packet lost!

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.pika_host(to), **PIKA_CON_PARAMETERS))
        channel = connection.channel()
        channel.queue_declare(queue=f'node{to}')
        channel.basic_publish(exchange='', routing_key=f'node{to}',
                              body=f"{self.current_node}{'###$$###'}{msg}".encode())
        connection.close()

    def start_second_phase(self):
        log(f'second phase started!')
        message = "CRQ" + "#" + self.current_node + "#" + str(self.find_priority_from_config_file()) + "#" + "0"
        for n in self._world_map.nodes:
            self.send_message(n, message)

    def start_first_phase(self):
        log(f'first phase started!')
        self.is_active = True if self.find_priority_from_config_file() == 3 else False
        self.active_sources = self.find_active_sources()

        if self.is_active:
            log(f'successfully filtered!')
            self.start_second_phase()
            # print(self.active_sources)
        else:
            log(f'rejected!')
            log(f'waiting for CRQ messages!')

    @property
    def neighbors(self) -> list:
        return list(self._world_map.neighbors(self.current_node))

    @property
    def edges(self) -> EdgeDataView:
        return self._world_map.edges(self.current_node)

    @property
    def edges_with_data(self) -> EdgeDataView:
        return self._world_map.edges(self.current_node, data=True)

    def get_edge_data(self, u, v, key=None, default=None):
        return self._world_map.get_edge_data(u, v).get(key, default)

    def find_priority_from_config_file(self):
        f = open(args.config)
        return int(f.readlines()[int(self.current_node) - 1].split()[-1])

    def find_active_sources(self):
        actives = []
        f = open(args.config)
        for line in f.readlines():
            if int(line.split()[-1]) == 3:
                actives.append(line.split()[0].split(":")[0])
        return actives

    def __init__(self):
        if args.force_node is None:
            self.current_node = socket.gethostname().replace('node', '')
        else:
            self.current_node = args.force_node

        self._world_map = nx.read_gml(args.network_gml)

        self.number_of_nodes_world_map = len(self._world_map.nodes)
        self.number_of_messages = 0
        self.is_active = None
        self.voted = False
        self.votes = 0
        self.active_sources = []


class SimulatorOnlyNeighbors(SimulatorFullView):
    name = 'simulator-only-neighbours'

    def start_first_phase(self):
        raise NotImplementedError

    def send_message(self, to, msg):
        if to not in self.neighbors and to != self.current_node:
            raise ValueError('Only can send message to neighbors!')
        return super().send_message(to, msg)

    def __init__(self):
        super().__init__()


world = AbstractWorld.get_instance()
