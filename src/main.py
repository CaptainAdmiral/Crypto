from network_emulator.net_connection import*
from protocol import*
from protocol import protocol_factory
from network_emulator import network
from script import run

def register_protocols():
    protocol_factory.register_protocols(StdProtocol)

def initialize_network():
    pass

if __name__ == "main":
    register_protocols()
    initialize_network()
    asyncio.run(run())