from enum import Enum
from typing import Any, Callable, Generic, NamedTuple, Self, TypeAlias, TypeVar, cast
from abc import ABC, abstractmethod
import json
from pydantic import BaseModel
from network_emulator import NetConnection
from protocol.std_protocol import StdProtocol

class ControlPacket(Enum):
    ACKNOWLEDGEMENT = 'ok'

class DialogueException(Exception):
    ...

class DialogueTreeException(Exception):
    ...

ExpectedTypes: TypeAlias = str | ControlPacket | type[BaseModel] | Callable[[Any], bool]
T = TypeVar('T', bound='ExpectedTypes')

class Dialogue():

    def __init__(self, header: str):
        self.header = header
        self.dialogue = None

    @property
    def length(self) -> int:
        if self.dialogue is None:
            return 0
        length=0
        curNode = self.dialogue
        while curNode.child is not None:
            length += 1
            curNode = curNode.child
        return length

    class _AbstractDialogueStep(ABC):

        def __init__(self):
            self.child = None
            self.actions: list[Callable[[Any]]] = []

        def do(self, action: Callable[[Any]]) -> Self:
            '''Executes a callback after this node executes successfully.
            This does not add a new node to the dialogue tree.'''
            self.actions.append(action)
            return self

    class _Reply(_AbstractDialogueStep):

        def __init__(self, reply: Any):
            super().__init__()
            self._child = None
            self.reply = reply
            
        def execute(self, net_connection: NetConnection):
            net_connection.write_out(self.reply)

        def expect(self, expect: ExpectedTypes):
            '''Validates the next response from the dialogue partner'''
            self._child = Dialogue._Expect(expect)
            return self._child

        def expect_acknowledgement(self):
            '''Expects an acknowledgement packet'''
            self._child = Dialogue._Expect(ControlPacket.ACKNOWLEDGEMENT)
            return self._child

    class _Expect(Generic[T], _AbstractDialogueStep):

        def __init__(self, expect: ExpectedTypes, *, unmet: Callable | None = None):
            super().__init__()
            self.child = None
            self.expect = expect
            self.actions: list[Callable[[T]]] = []
            self.err_func = unmet
            
        async def execute(self, net_connection: NetConnection):
            try:
                data_str = await net_connection.read_in()
                data = None if data_str is None else json.loads(data_str)

                if isinstance(self.expect, str) and self.expect != data_str:
                    raise DialogueException(f"Expected {self.expect} but got {data_str}")

                if isinstance(self.expect, Callable):
                    if not self.expect(data):
                        raise DialogueException(f"Invalid response: {data_str}")

                if isinstance(self.expect, type):
                    if data is None:
                        raise DialogueException(f"Empty response!") 
                    model = self.expect(**cast(dict, data))

                for action in self.actions:
                    action(cast(T, self.expect))

            except Exception as e:
                return False
            
        def do(self, action: Callable[[T]]) -> Self:
            self.actions.append(action)
            return self
            
        def reply(self, reply: str | BaseModel | ControlPacket):
            '''Sends a reply packet'''
            rep = reply
            if isinstance(reply, BaseModel):
                rep = json.dumps(reply.dict())
            self.child = Dialogue._Reply(str(rep))
            return self.child

        def acknowledge(self):
            '''Sends an acknowledgement packet'''
            return self.reply(ControlPacket.ACKNOWLEDGEMENT)
    
    def send_header(self):
        '''Initializes the root of the dialogue tree with a reply node sending the header'''
        self.dialogue = Dialogue._Reply(self.header)
        return self.dialogue
    
    def accept_header(self):
        '''Initializes the root of the dialogue tree with an expect node expecting the header'''
        self.dialogue = Dialogue._Expect(self.header)
        return self.dialogue

def register_dialogue(initial: Dialogue, response: Dialogue):
    '''Registers a dialogue for use by the standard protocol. This was designed as a convenience function for internal use only,
    nodes running deviant protocols have no need to register their dialogues with the standard protocol'''

    if(initial.header == response.header):
        raise DialogueTreeException('Header mismatch')
    if(not isinstance(initial.dialogue, Dialogue._Reply)):
        raise DialogueTreeException('Initiating dialogue is set up to expect a resonse as its first node')
    if(not isinstance(initial.dialogue, Dialogue._Reply)):
        raise DialogueTreeException('Responding dialogue is set up to send a message as its first node')
    if(0 <= (initial.length - response.length) <= 1):
        raise DialogueTreeException('dialogue length mismatch between initial and responder')
    StdProtocol.dialogueRegistry[initial.header] = (initial, response)