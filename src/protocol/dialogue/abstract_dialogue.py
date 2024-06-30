from enum import Enum
from typing import Any, Callable, Generic, Optional, Self, TypeAlias, TypeVar, cast
from abc import ABC
import json
from pydantic import BaseModel
from network_emulator import NetConnection
from protocol.abstract_protocol import AbstractProtocol
from protocol.std_protocol import StdProtocol

class ControlPacket(Enum):
    ACKNOWLEDGEMENT = 'ok'

class DialogueException(Exception):
    '''Exception with execution of dialogue'''
    ...

class DialogueGraphException(Exception):
    '''Exception when building dialogue graph'''
    ...

P = TypeVar('P', bound=AbstractProtocol)
'''Protocol Type'''

T = TypeVar('T', bound=Any, contravariant=True)
'''State Type'''

DataType: TypeAlias = str | ControlPacket | BaseModel

class Dialogue(Generic[P, T]):
    def __init__(self, header: str, state: T = None, Protocol: type[P] = StdProtocol):
        self.header = header
        self.dialogue = None
        self.state = state

    def new_node(self, reply):
        '''Should be used to extend an existing dialogue graph. To initiate a new dialogue graph use send_header / accept_header'''
        return _Reply[P, T](reply)
    
    def send_header(self):
        '''Initializes the root of the dialogue tree with a reply node sending the header'''
        self.dialogue = _Reply[P, T](self.header)
        return self.dialogue
    
    def accept_header(self):
        '''Initializes the root of the dialogue tree with an expect node expecting the header'''
        self.dialogue = _Expect[P, T](self.header)
        return self.dialogue
    
class _AbstractDialogueStep(Generic[P, T], ABC):

    def __init__(self):
        self._child: Optional[_AbstractDialogueStep] = None

    def get_child(self):
        return self._child
    
    def join(self, node: '_AbstractDialogueStep') -> '_AbstractDialogueStep':
        '''Extends the dialogue graph at this node by taking the given node as a child
        :param node: the node to join as a child of this one
        :return: node (for method chaining)
        '''
        self._child = node
        return self._child
    
class _Fork(_AbstractDialogueStep[P, T]):

    def __init__(self, fork: Callable[[DataType, Optional[T], P]], children: dict[str, '_Reply[P, T]']):
        super().__init__()
        self._children = children
        self.fork = fork
        
    def execute(self, data: DataType, state: T, protocol: P) -> Self:
        self._child = self._children[self.fork(data, state, protocol)]
        return self

class _Reply(_AbstractDialogueStep[P, T]):     

    def __init__(self, reply: DataType | Callable[[DataType, T, P], str]):
        super().__init__()
        self._child = None
        self.reply = reply
        
    def execute(self, net_connection: NetConnection, data: DataType, state: T, protocol: P):
        rep = None
        if isinstance(self.reply, BaseModel):
            rep = json.dumps(self.reply.dict())
        elif isinstance(self.reply, Callable):
            rep = self.reply(data, state, protocol)

        net_connection.write_out(rep)

    def expect(self, expect: str | ControlPacket | type[BaseModel] | Callable[[DataType, T, P], DataType], *, unmet: Callable | None = None):
        '''Validates the next response from the dialogue partner.
        :param unmet: Callback for if the expectation is not met'''

        self._child = _Expect[P, T](expect, unmet=unmet)
        return self._child

    def expect_acknowledgement(self):
        '''Expects an acknowledgement packet'''
        return self.expect(ControlPacket.ACKNOWLEDGEMENT)

class _Expect(_AbstractDialogueStep[P, T]):

    def __init__(self, expect: str | ControlPacket | type[BaseModel] | Callable[[DataType, T, P], DataType], *, unmet: Callable | None = None):
        super().__init__()
        self.expect = expect
        self.err_func = unmet
        self.data = None
        self.actions: list[Callable[[DataType, T, P]]] = []
        
    async def execute(self, net_connection: NetConnection, state: T, protocol: P) -> DataType:
        processed_data = None

        data_str = await net_connection.read_in()
        data = None if data_str is None else json.loads(data_str)
        if data is None:
            raise DialogueException(f"Empty response!")

        if isinstance(self.expect, str) and self.expect != data_str:
            processed_data = data
            raise DialogueException(f"Expected {self.expect} but got {data_str}")
        elif isinstance(self.expect, type) and issubclass(self.expect, BaseModel):
            processed_data = self.expect(**cast(dict, data))
        elif isinstance(self.expect, Callable):
            f = self.expect
            output = f(data, state, protocol)
            if output:
                raise DialogueException(f"Invalid response: {data_str}")
            processed_data = output
        else:
            raise TypeError('Unhandled type in expect step')
        
        return processed_data
        
    def reply(self, reply: DataType | Callable[[DataType, T, P]]):
        '''Sends a reply packet'''

        self._child = _Reply[P, T](reply)
        return self._child

    def acknowledge(self):
        '''Sends an acknowledgement packet'''
        return self.reply(ControlPacket.ACKNOWLEDGEMENT)
    
    def fork(self, f: Callable[[DataType, Optional[T], P]], children: dict[str, _Reply[P, T]]):
        '''Forks the dialgoue graph. Can refer to previous nodes if dialogue needs to be looped.
        :param f: Callable of signature [(data, state) => key] that at dialog execution returns a key for which child the dialogue parser should execute next'''

        self._child = _Fork[P, T](f, children)
        return self._child
    
    def do(self, action: Callable[[DataType, T, P]]) -> Self:
        '''Executes a callback after this node executes successfully.
        This does not add a new node to the dialogue tree.'''
        self.actions.append(action)
        return self

def register_dialogue(initial: Dialogue, response: Dialogue):
    '''Registers a dialogue for use by the standard protocol. This was designed as a convenience function for internal use only,
    nodes running deviant protocols have no need to register their dialogues with the standard protocol'''

    if(initial.header == response.header):
        raise DialogueGraphException('Header mismatch')
    if(not isinstance(initial.dialogue, _Reply)):
        raise DialogueGraphException('Initiating dialgue does not start with a reply node')
    if(not isinstance(initial.dialogue, _Expect)):
        raise DialogueGraphException('Responding dialogue does not start with an expect node')
    StdProtocol.dialogue_registry[initial.header] = (initial, response)