#! /usr/bin/python3
import os
import pathlib
import subprocess
import sys
from datetime import datetime
import argparse
from functools import partial
from typing import Any

import networkx as nx
from jinja2 import Environment, FileSystemLoader
from matplotlib import pyplot as plt
from networkx.drawing.nx_pydot import write_dot


def add_boolean(self, arg_name: str, dest: str, default: Any, **extra):
    if arg_name.startswith('--'):
        arg_name = arg_name.replace('--', '')

    self.add_argument(f"--{arg_name}", dest=dest, action='store_true', **extra)
    self.add_argument(f"--no-{arg_name}", dest=dest, action='store_false', **extra)
    self.set_defaults(**{dest: default})


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_boolean = partial(add_boolean, parser)

parser.add_argument('--input', dest='input_file', help='Gets the input file (otherwise uses stdin)')
parser.add_argument('--graph-image-format', dest='graph_image_format', default='png',
                    help='(default: png) Sets extension for network\'s image.')
parser.add_argument('--show-graph', dest='show_graph_image', action='store_true',
                    help="Shows the generated graph in a matplotlib windows.")
parser.add_boolean('--directed-graph', dest='directed_graph', default=False,
                   help="Sets whether the network is directed or not. Default graph is not directed.")
parser.add_argument('--stop-time', dest='stop_time', default='10s',
                    help='The simulated time at which simulated processes are sent a SIGKILL signal.')
parser.add_argument('--shadow-template', dest='shadow_template_name', help='Chooses a shadow template.',
                    default='base.yml.j2')
parser.add_argument('--run', dest="run_at_end", action='store_true', help='Runs simulator at the end.',
                    default=True)
parser.add_argument('--docker-image', dest="docker_image", help='The docker image to run shadow simulation',
                    default='dis2021')
parser.add_argument('--debug', dest="debug", action='store_true', help='Debug Mode',
                    default=False)
parser.add_argument('--stdout', dest="stdout_enabled", action='store_true', help='Show output in stdout',
                    default=False)
parser.add_argument('--default-latency', dest='default_latency', default='10 ms', help='''
The latency that will be added to packets traversing this edge. This value is used as a weight while running Dijkstra's 
shortest path algorithm. The format of the string specifies the latency and its unit, e.g., 10 ms. If a unit is not 
specified, it will be assumed that it is in the base unit of "seconds". The latency must not be 0.
''')
parser.add_argument('--default-packet-loss', dest='default_packet_loss', default=0., type=float, help='''
A fractional value between 0 and 1 representing the chance that a packet traversing this edge will get dropped.
''')
parser.add_argument('--downstream', dest="down_stream", default="10 Mbit")
parser.add_argument('--upstream', dest="up_stream", default="10 Mbit")
parser.add_boolean('--shortest-path', dest='shortest_path', default=False, help='''(default: false) When routing 
packets, follow the shortest path rather than following a direct edge between nodes. If false, the network graph is 
required to be complete.''')
parser.add_boolean('--network-loops', dest='network_loops', default=True,
                   help='Set to true if we should have auto self loops')
parser.add_argument('--simulator', dest="simulator", default="process", help='The simulator to simulate the network '
                                                                             'with options: shadow, process')
args = parser.parse_args()


def log(msg, level='info'):
    if args.debug:
        print(f'[{level}] {msg}', file=sys.stderr)


def convert_attributes(k: str, v: str) -> Any:
    return {
        'packet_loss': float
    }.get(k, lambda x: x)(v)


def parse_line(line: str) -> dict:
    items = line.split()
    v, u, weight = [int(_) for _ in items[:3]]
    result = {
        "v_of_edge": v,
        "u_of_edge": u,
        "weight": weight,
        "latency": args.default_latency,
        "packet_loss": args.default_packet_loss
    }

    if len(items) >= 3:
        for _ in items[3:]:
            k, v = _.split("=")
            result[k] = convert_attributes(k, v)

    return result


def add_nodes(g: [nx.Graph, nx.DiGraph], num_of_nodes):
    for i in range(1, num_of_nodes + 1):
        g.add_node(i, host_bandwidth_up=args.up_stream, host_bandwidth_down=args.down_stream)
        if args.network_loops:
            g.add_edge(i, i, weight=0, latency=args.default_latency, packet_loss=args.default_packet_loss)


def generate_graph() -> [nx.Graph, nx.DiGraph]:
    if args.directed_graph:
        g = nx.DiGraph()
    else:
        g = nx.Graph()

    if args.input_file is None:
        add_nodes(g, int(input()))
        for _ in sys.stdin:
            g.add_edge(**parse_line(_))
    else:
        with open(args.input_file) as f:
            add_nodes(g, int(f.readline()))
            for _ in f.readlines():
                g.add_edge(**parse_line(_))

    plt.plot()
    nx.draw(g, with_labels=True)
    plt.savefig(f"{tempdir}/network.{args.graph_image_format}")
    write_dot(g, f"{tempdir}/network.dot")
    nx.write_gml(g, f"{tempdir}/network.gml")
    if args.show_graph_image:
        plt.show()

    return g


def generate_shadow_configuration(**extra):
    env = Environment(loader=FileSystemLoader('shadow_templates'))
    template = env.get_template(args.shadow_template_name)
    with open(f"{tempdir}/shadow.yml", 'w') as f:
        f.write(template.render(
            stop_time=args.stop_time,
            tempdir=tempdir,
            log_level='debug' if args.debug else 'info',
            **extra
        ))


def run_simulation_shadow():
    workspace = pathlib.Path(tempdir).parent.parent.absolute()
    command = f'docker run --rm --privileged --shm-size="1g" -v {workspace}:/workspace --log-driver=none ' \
              f'-e GID={os.getgid()} ' \
              f"{args.docker_image} " \
              "--interpose-method=ptrace " \
              f"-l {'debug' if args.debug else 'info'} " \
              f"--use-shortest-path {'true' if args.shortest_path else 'false'} " \
              f"--data-directory {tempdir}/shadow.data " \
              f"{tempdir}/shadow.yml"

    if not args.stdout_enabled:
        with open(f"{tempdir}/log.out", 'w') as f:
            subprocess.call(command, shell=True, stdout=f, stderr=f)
    else:
        subprocess.call(command, shell=True)


def run_simulation_process():
    global graph
    num_nodes = graph.number_of_nodes()
    workspace = pathlib.Path(tempdir).absolute()
    workspace.joinpath('logs').mkdir(exist_ok=True)

    processes = []
    for i in range(1, num_nodes + 1):
        stdout = open(f'{workspace}/logs/node{i}.stdout', 'w')
        stderr = open(f'{workspace}/logs/node{i}.stderr', 'w')

        log(f'starting node{i}.')
        p = subprocess.Popen(' '.join([
            'python',
            workspace.parent.parent.absolute().joinpath('node.py').__str__(),
            f'--force-node {i}',
            '--pika-host localhost',
            '--world simulator-only-neighbours',
            '--network ' + workspace.joinpath('network.gml').absolute().__str__(),
            '--simulate-network-parameters'
        ]), shell=True, stdout=stdout, stderr=stderr)
        processes.append(p)

    log('start waiting for processes...')
    for p in processes:
        p.wait()


def run_simulation():
    log('starting simulation...')
    try:
        return {
            'shadow': run_simulation_shadow,
            'process': run_simulation_process
        }[args.simulator]()
    except KeyError:
        raise NotImplementedError


if __name__ == '__main__':
    # Create tempdir
    log('creating temp directory.')
    tempdir = "output/" + datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    pathlib.Path(tempdir).mkdir(parents=True)

    log('generating graph')
    graph = generate_graph()
    generate_shadow_configuration(
        num_nodes=graph.number_of_nodes()
    )

    if args.run_at_end:
        try:
            run_simulation()
        except KeyboardInterrupt as e:
            log('received keyboard interrupt')
            raise e
