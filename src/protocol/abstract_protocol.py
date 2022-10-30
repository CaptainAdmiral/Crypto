from abc import ABC, abstractmethod
from network_emulator import NetConnection

class AbstractProtocol(ABC):

    def __init__(self, node):
        self._node = node

    @abstractmethod
    def weight() -> float:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def request_net_connection(self, net_con: NetConnection):
        pass