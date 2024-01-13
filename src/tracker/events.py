from dataclasses import dataclass
from abc import abstractmethod

@dataclass
class Event:
    event: str

    @abstractmethod
    def handle(self, contract, provider, IPFSClient):
        pass

@dataclass
class PacketForged(Event):
    blacksmith: str
    packetId: int

    def handle(self, contract, provider, IPFSClient):
        super().handle()
        

@dataclass
class PacketOpened(Event):
    opener: str
    prompts: list

    def handle(self, contract, provider, IPFSClient):
        return super().handle()

@dataclass
class CreateImage(Event):
    creator: str
    card: int

    def handle(self, contract, provider, IPFSClient):
        return super().handle()

@dataclass
class WillToBuyEvent(Event):
    buyer: str
    seller: str
    value: float


@dataclass
class WillToBuyPacket(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient):
        return super().handle()

@dataclass
class WillToBuyPrompt(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient):
        return super().handle()

@dataclass
class WillToBuyImage(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient):
        return super().handle()


@dataclass
class TransferEvent(Event):
    buyer: str
    seller: str
    id: int

@dataclass
class PacketTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient):
        return super().handle()

@dataclass
class PromptTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient):
        return super().handle()

@dataclass
class ImageTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient):
        return super().handle()


def get_event_class(event_name):
    event_class = globals()[event_name]
    return event_class