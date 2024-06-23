from enum import Enum


class DialogueEnum(str, Enum):
    HANDSHAKE = 'handshake'
    REQUEST_NODE_LIST = 'request_node_list'