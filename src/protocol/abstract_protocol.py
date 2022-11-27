from abc import ABC, abstractmethod
from network_emulator import NetConnection

class AbstractProtocol(ABC):

    def __init__(self, node):
        self._node = node

    @abstractmethod
    def weight() -> float:
        '''The weight with which this protocol will be chosen to populate the network.
        
        The standard protocol has a weight of 1.0'''
        pass

    @abstractmethod
    def request_net_connection(self, net_con: NetConnection):
        pass