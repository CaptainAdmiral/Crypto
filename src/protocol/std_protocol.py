from network_emulator import NetConnection
from protocol import AbstractProtocol

class ext_node():

    def __init__(self, timestamp, address):
        self.timestamp = timestamp
        self.address = address

class StdProtocol(AbstractProtocol):

    def __init__(self, node):
        super().__init__(node)
        self.public_key = None
        self.private_key = None
        self.node_list: ext_node = []
        self.net_connections: list[NetConnection] = []

    def weight() -> float:
        return 1.0

    def request_net_connection(self, net_con: NetConnection):
        self.net_connections.append(net_con)
        net_con.open()