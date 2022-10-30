from protocol import*
from numpy import random

_protocol_types: set[type[AbstractProtocol]] = set()

def register_protocol(protocol: type[AbstractProtocol]) -> None:
    '''Registers a protocol so that it will be randomly used by nodes in the network according to weight'''
    _protocol_types.add(protocol)

def get_protocol(node) -> AbstractProtocol:
    return random.choice(_protocol_types,
        p=[Protocol.weight() for Protocol in _protocol_types])(node)