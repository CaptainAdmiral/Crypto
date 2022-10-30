from network_emulator import Node, NetConnection
from protocol import ServerProtocol


class Server(Node):
    '''A centralized server for dealing with information that does not require a decentralized broadcast protocol
    (directed acyclic graph, decentralized message broadcasting etc). Information that is cryptographically signed
    and can be assumed to be incomplete is fine to be distributed from a centralized point (Anyone can take on the
    role of this server)
    
    Currently the only information that needs to be distributed this way is when updating nodes about the verification
    network'''

    def __init__(self):
        super().__init__(ServerProtocol())


    