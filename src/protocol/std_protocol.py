from dataclasses import dataclass
from network_emulator import NetConnection
from protocol import AbstractProtocol
from protocol.dialogue.abstract_dialogue import Dialogue

@dataclass
class PublicNodeData:
    '''The public data about the node as appears on the node list.'''
    address: int
    public_key: str
    timestamp: float
    
class StdProtocol(AbstractProtocol):

    dialogue_registry: dict[str, tuple[Dialogue, Dialogue]] = {}

    def __init__(self, node):
        super().__init__(node)
        self.net_connections: list[NetConnection] = []
        self.node_list: list[PublicNodeData] = []
        self.address=node.address,
        self.public_key=None,
        self.private_key=None,
        self.timestamp=None

    @staticmethod
    def weight() -> float:
        return 1.0

    def request_net_connection(self, net_con: NetConnection):
        self.net_connections.append(net_con)
        net_con.open()

    def execute_dialogue_graph(self, net_con: NetConnection, Dialogue):
        ...