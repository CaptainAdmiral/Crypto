import asyncio
from typing import Self
from node import Node
from enum import Enum
from settings import NETWORK_DELAY, NETWORK_DELAY_VARIABILITY
import numpy as np

class NetConnection():
    """Net connection emulator class for sending packets between two nodes on the network.
    
    NetConnections are implemented as pairs of instances where each NetConnection writes it's data out to it's inverse and vica versa.
    """

    _network_trafic_tasks = set()

    class Packets(Enum):
        CLOSE = 'close'

    class NetConnectionClosedException(Exception):
        """Raised when write opperations are attempted on a closed NetConnection """        
        pass

    class NoInverseException(Exception):
        """Raised when an opperation is attempted on a NetConnection that does not have an inverse """ 

        def __init__(self, message=''):
            super().__init__("NetConnection does not have an inverse! Please make sure you assign the inverse to another node first using get_inverse()"+'\n'+message)

    def __init__(self, node: Node, other_node: Node, header: str = '', *, inverse=None):
        self._header = header
        self.is_open = False
        self.in_waiting = False
        self._inverse = inverse

        if not self._inverse:
            self._inverse = NetConnection(self._other_node, self._node, self._header, inverse=self) 

        self._node = node
        self._other_node = other_node
        self._read_buffer = []

        self._read_event = asyncio.Event()
        self._outgoing_packets = set()

    def __enter__(self):
        self.open()

    def __exit__(self):
        self.close()

    def get_inverse(self) -> Self:
        """Returns the inverse net connection to this net connection

        Raises:
            self.NoInverseException: if the inverse for this net connection does not exist

        Returns:
            SelfType: inverse NetConnection
        """        
        if not self._inverse:
            raise self.NoInverseException()

        return self._inverse

    def get_header(self) -> str:
        return self._header

    def open(self):
        """Marks a NetConnection as open for read / write"""

        if not self._inverse:
            raise self.NoInverseException("This error was raised because the NetConnection was opened but was not connected to another node. Perhaps the connection has already been closed?")

        self.is_open = True
        if not self._inverse.is_open:
            self._inverse.open()

    def close(self):
        """Writes out a close packet and then closes the NetConnection.
        A closed NetConnection undergoes certain cleanup functions cannot be reopened again, please use a new NetConnection instance for this."""

        self.write_out(self.Packets.CLOSE)
        self._inverse = None
        self.is_open = False

    async def read_in(self, blocking=True) -> str | None:
        """Reads in a packet from the NetConnection read buffer

        Returns:
            str: packet
        """

        if not self._read_buffer:
            if blocking:
                await self._read_event.wait()
            else:
                return None

        s = self._read_buffer.pop()
        if not self._read_buffer:
            self._read_event.clear()
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

        if not self._inverse:
            raise self.NoInverseException()

        try:
            task = asyncio.create_task(self._write_to_inverse(out))
            self._network_trafic_tasks.add(task)
            task.add_done_callback(lambda t : self._network_trafic_tasks.remove(t))
        except Exception as e:
            pass


    async def _write_to_inverse(self, out: str):
        await asyncio.sleep(np.random.normal(NETWORK_DELAY, NETWORK_DELAY*NETWORK_DELAY_VARIABILITY))
        self._inverse.receive_packet(str(out))

    def receive_packet(self, pkt: str):  
        self.in_waiting = True
        self._read_buffer.append(str(pkt))
        self._read_event.set()