from network_emulator import NetConnection
from protocol.abstract_protocol import AbstractProtocol

class ServerProtocol(AbstractProtocol):
    
    def __init__(self):
        self.net_connections = []

    def weight() -> float:
        return 0

    def update(self) -> None:
        pass

    def request_net_connection(self, net_con: NetConnection):
        self.net_connections.append(net_con)
        net_con.open()