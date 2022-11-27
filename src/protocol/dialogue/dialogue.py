from enum import Enum
from typing import Callable, Self, TypeVar
from abc import ABC
from pydantic import BaseModel
from network_emulator import NetConnection

DialogueType = TypeVar("DialogueType", bound="Dialogue")
class Dialogue():

    class ControlPackets(Enum):
        ACKNOWLEDGEMENT = 'ok'

    def __init__(self, responseTo: str = None):
        self.responseTo = responseTo
        self.net_connection: NetConnection | None = None
        self.child = None

    def initiate_dialogue(self, dialogue: str):
        self.child = Dialogue._Reply(dialogue)
        return self.child

    class _AbstractDialogueStep(ABC):

        def __init__(self, parent: Self | DialogueType | None):
            self._parent = parent

        def end_dialogue(self):
            parent = self._parent
            while parent._parent is not None:
                parent = parent._parent
            return parent

    class _Reply(_AbstractDialogueStep):
        def __init__(self, parent, reply: str | BaseModel):
            self._parent = parent
            self._child = None
            self.reply = reply
            
        def execute(self, net_connection: NetConnection):
            pass

        def expect(self, expect: str):
            self._child = Dialogue._Expect(expect)
            return self._child

        def expect_acknowledgement(self):
            self._child = Dialogue._Expect(Dialogue.ControlPackets.ACKNOWLEDGEMENT)
            return self._child

    class _Expect(_AbstractDialogueStep):
        def __init__(self, parent, expect: str | BaseModel):
            self._parent = parent
            self.child = None
            self.expect = expect
            
        async def execute(self, net_connection: NetConnection):
            pass

        def reply(self, reply: str | BaseModel):
            self.child = Dialogue._Reply(reply)
            return self.child

        def acknowledge(self):
            self.child = Dialogue._Reply(Dialogue.ControlPackets.ACKNOWLEDGEMENT)
            return self.child

        def do(self, func: Callable[[str | BaseModel], str | BaseModel]):
            return Dialogue._Expect(func(self.expect))