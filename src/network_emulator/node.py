import itertools
from protocol import AbstractProtocol
from net_connection import NetConnection

class Node():
    _address_gen = itertools.count()

    def __init__(self, protocol: AbstractProtocol):
        self.address = next(self._address_gen)
        self.protocol = protocol
        
    def update(self):
        self.protocol.update()
    
    def request_net_connection(self, net_con: NetConnection):
        inverse = net_con.get_inverse()
        self.protocol.request_net_connection(inverse)