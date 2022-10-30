from network_emulator.net_connection import*
from protocol import*
from protocol import protocol_factory
from network_emulator import network
import numpy as np

is_running = True


def register_protocols():
    protocol_factory.register_protocol(StdProtocol)

def update_nodes():
    for i in np.random.permutation(len(network.nodes)):
        network.nodes[i].update()

if __name__ == "main":
    register_protocols()

    while is_running:
        update_nodes()