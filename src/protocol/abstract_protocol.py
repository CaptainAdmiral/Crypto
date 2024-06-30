from abc import ABC, abstractmethod
import network_emulator as ne

class AbstractProtocol(ABC):

    def __init__(self, node: ne.Node):
        self._node = node
    
    @staticmethod
    @abstractmethod
    def weight() -> float:
        '''The weight with which this protocol will be chosen to populate the network.
        
        The standard protocol has a weight of 1.0'''
        pass

    @abstractmethod
    def request_net_connection(self, net_con: ne.NetConnection):
        pass