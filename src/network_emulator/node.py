import itertools
import protocol
import net_connection as nc

class Node():
    _address_gen = itertools.count()

    def __init__(self, protocol: protocol.AbstractProtocol):
        self.address = next(self._address_gen)
        self.protocol = protocol
    
    def request_net_connection(self, net_con: nc.NetConnection):
        inverse = net_con.get_inverse()
        self.protocol.request_net_connection(inverse)