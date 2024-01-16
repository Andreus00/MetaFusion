from dataclasses import dataclass
from abc import abstractmethod, ABC
from .data import Data, Packet, Image, Prompt
from typing import List
from .data import Data
from ..utils.utils import from_int_to_hex_str, from_str_hex_to_int_str

PACKET_SIZE = 8
NUM_PROMPT_TYPES = 6


'''
0) CollectionForged: When a collection is created. Only the owner of the contract can forge packets.
1) Packet forged: When packets are minted in blockchain

2) Packet opened: When packets are opened on blockchain (and prompts are created, this is handled in a different event). Packets are still not in IPFS.
3) Prompt created: When a prompt is created in IPFS by oracle

4) Create Image: When an image is created in blockchain. Images are still not in IPFS.
5) Image created: When an image is created in IPFS by oracle
'''


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
        '''
        Create a packet in the database
        '''
        packet = Packet()
        packet.initWithParams(id=self.packetId, userIdHex=self.blacksmith, data=data)
        return data

@dataclass
class PacketOpened(Event):
    opener: str
    prompts: List[int]
    uri: List[str]  # uri of prompts 

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''
        Delete the packet burnt from the database and create the prompts without IPFS hash
        ID: 0-12 collection
        13-15 prompt type
        16-28 packet id in collection
        29-31 sequence number of the prompt in packet
        [31, 30, 29, 28, 27, 26, 25, 24, 23, 22, ... , 3, 2, 1, 0]
        '''
        prompt = self.prompts[0]
        # get collection id then
        # get packet id in collection
        packet_id = prompt & 0x1fff1fff
        data.remove_packet_from(packet_id=packet_id, user_id=self.opener)

        for prompt, uri in zip(self.prompts, self.uri):
            # TODO: create prompt in the database
            pass
@dataclass
class PromptCreated(Event):
    opener: str
    prompt: int
    IPFSCid: int

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''
        Add the IPFS hash to the prompt in the database and the "name" of the prompt
        '''
        prompt = Prompt()
        prompt_name = IPFSClient.http_client.get(self.IPFSCid)
        prompt.initWithParams(self.prompt, hash=str(self.IPFSCid), 
                    name=prompt_name, 
                    userIdHex=self.opener, 
                    data=data) #Not sure this is correct

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
                            userIdHex=from_int_to_hex_str(int(self.creator))) # Is this correct?
        image.writeToDb(data)
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
    value: int  # value of the NFT

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