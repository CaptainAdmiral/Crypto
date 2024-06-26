from network_emulator import Node, Server, NetConnection

the_server = Server()
nodes: dict[int, Node] = {}

def connect_to_node(self_node: Node, other_node: Node) -> NetConnection:
    nc = NetConnection(self_node, other_node)
    other_node.request_net_connection(nc)
    return nc