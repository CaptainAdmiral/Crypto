from node import Node
from enum import Enum

class NetConnection():
    """Net connection emulator class for sending string packets between two nodes on the network.
    
    NetConnections are implemented as pairs of instances where each NetConnection writes it's data out to it's inverse and vica versa.
    It is not recommended to instance the NetConnection class directly, instead please add a network method that handles the get_inverse() appropriately.
    """    

    class Packets(Enum):
        CLOSE = 'close'

    class NetConnectionClosedException(Exception):
        """Raised when write opperations are attempted on a closed NetConnection """        
        pass

    class NoInverseException(Exception):
        """Raised when a NetConnection is opened without first assigning it's inverse to anything """ 

        def __init__(self, message=''):
            super().__init__("NetConnection does not have an inverse! Please make sure you assign the inverse to another node first using get_inverse()"+'\n'+message)

    def __init__(self, node: Node, other_node: Node, header: str = ''):
        self._header = header
        self.is_open = False
        self.in_waiting = False
        self._inverse = None
        self._node = node
        self._other_node = other_node
        self._read_buffer = []

    def get_inverse(self):
        """Returns a new NetConnection with the read in / write out methods swapped to correspond to this NetConnection,
        or the existing NetConnection if this method has already been called before.

        Returns:
            SelfType: inverse NetConnection
        """        
        if not self._inverse:
            self._inverse = NetConnection(self._other_node, self._node, self._header) # Warning! Make sure the circular reference here is always removed before object falls out of scope
        self._inverse._inverse = self

        return self._inverse

    def get_header(self):
        return self._header

    def open(self):
        """Marks a NetConnection as open for read / write"""

        if not self._inverse:
            raise self.NoInverseException("This error was raised because the NetConnection was opened but was not connected to another node with request_net_connection")

        self.is_open = True
        if not self._inverse.is_open:
            self._inverse.open()

    def close(self):
        """Writes out a close packet and then closes the NetConnection"""

        self.write_out(self.Packets.CLOSE)
        self._inverse = None
        self.is_open = False

    def read_in(self) -> str:
        """Reads in a packet from the NetConnection read buffer

        Returns:
            str: packet
        """        
        s = self._read_buffer.pop()
        if not self._read_buffer:
            self.in_waiting = False
        return s

    def write_out(self, out):
        """Writes out a packet to the read buffer of the corresponding NetConnection

        Args:
            out (Any): Packet to write out. Will cast to string first.

        Raises:
            NetConnectionClosedException: if the NetConnection is closed
        """        
        if not self.is_open:
            raise self.NetConnectionClosedException("Cannot write to a closed NetConnection!")
        self._inverse.in_waiting = True
        self._inverse._read_buffer.append(str(out))