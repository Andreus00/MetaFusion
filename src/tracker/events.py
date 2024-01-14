from dataclasses import dataclass
from abc import abstractmethod, ABC
from .data import Data, Packet, Image, Prompt
from typing import List
from .data import Data
from ..utils.utils import from_int_to_hex_str, from_str_hex_to_int_str

PACKET_SIZE = 8
NUM_PROMPT_TYPES = 6


@dataclass
class Event(ABC):
    event: str

    @abstractmethod
    def handle(self, contract, provider, IPFSClient, data: Data):
        pass

@dataclass
class PacketForged(Event):
    blacksmith: str
    packetId: int
    # uri: str

    def handle(self, contract, provider, IPFSClient, data: Data):
        packet = Packet()
        packet.initWithParams(id=self.packetId, userIdHex=self.blacksmith)
        data.add_packet_to(packet, (self.blacksmith))
        return data
        

@dataclass
class PromptCreated(Event):
    opener: str
    prompt: int
    IPFSCid: int

    def handle(self, contract, provider, IPFSClient, data: Data):
        prompt = Prompt()
        prompt_name = IPFSClient.http_client.get(self.IPFSCid)
        prompt.initWithParams(self.prompt, hash=str(self.IPFSCid), 
                    name=prompt_name, 
                    userIdHex=from_int_to_hex_str(int(self.opener)))
        data.add_prompt_to(prompt=prompt, user_id=int(self.opener))
        pass

@dataclass
class PacketOpened(Event):
    opener: str
    prompts: List[int]
    uri = List[str]  # uri of prompts 

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''Just delete the packet burnt, because it can't be never used
        ID: 0-12 collection
        13-15 prompt type
        16-28 packet id in collection
        29-31 sequence number of the prompt in packet
        [31, 30, 29, 28, 27, 26, 25, 24, 23, 22, ... , 3, 2, 1, 0]'''
        prompt = self.prompts.pop()
        # get collection id then
        # get packet id in collection
        packet_id = prompt & 0x1fff1fff
        data.remove_packet_from(packet_id=packet_id, user_id=self.opener)
        

@dataclass
class CreateImage(Event):
    creator: str
    card: int
    uri: str

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''
        address indexed creator, uint256 prompts, string uri
        '''

        image = Image()
        image.initWithParams(id=self.card, 
                            userIdHex=from_int_to_hex_str(int(self.creator),
                            hash=str(self.IPFSCid)))
        image.add_image_to(image, int(self.creator))
        return super().handle()

@dataclass
class ImageCreated(Event):
    creator: str
    card: int
    IPFSCid: int

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''
        address indexed creator, uint256 prompts, string uri
        '''

        image = Image()
        image.initWithParams(id=self.card, 
                            userIdHex=from_int_to_hex_str(int(self.creator),
                            hash=None))
        imageId = image.id >> 64
        for _ in range(NUM_PROMPT_TYPES):
            currentPromptId = imageId & 0xffffffff
            
            if currentPromptId != 0:
                data.remove_prompt_from(prompt_id=currentPromptId, user_id=int(self.creator))


            imageId = imageId >> 32
        return super().handle()

@dataclass
class WillToBuyEvent(Event):
    '''
    When this event is intercepted, the tracker should check if the buyer sent enought money.
    If so, the tracker should send the money to the seller and the item to the buyer.
    Otherwise, the tracker should emit a refund.
    '''
    buyer: str
    seller: str
    value: float


@dataclass
class WillToBuyPacket(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, data: Data):
        pass

@dataclass
class WillToBuyPrompt(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, data: Data):
        return super().handle()

@dataclass
class WillToBuyImage(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, data: Data):
        return super().handle()


@dataclass
class TransferEvent(Event):
    buyer: str
    seller: str
    id: int

@dataclass
class PacketTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient, data: Data):
        data.transfer_packet(self.id, self.seller, self.buyer)

@dataclass
class PromptTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient, data: Data):
        data.transfer_prompt(self.id, self.seller, self.buyer)
        

@dataclass
class ImageTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient, data: Data):
        data.transfer_image(self.id, self.seller, self.buyer)


def get_event_class(event_name):
    event_class = globals()[event_name]
    return event_class