from dataclasses import dataclass
from abc import abstractmethod, ABC
import ipfs_api
from ..db.data import Data, Packet, Image, Prompt
from typing import List
from ..db.data import Data
from ..utils.utils import *
import json
import ipfs_api
import numpy as np
from PIL import Image as Img

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

    def log(self, logger):
        attributes = "\n".join([f"{k}: {v}" for k, v in self.__dict__.items()])
        msg = f"""
                ====================
                {attributes}
                """
        logger.info(f"{msg}")

@dataclass
class PacketForged(Event):
    blacksmith: str
    packetId: int

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

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''
        Delete the packet burnt from the database and create the prompts without IPFS hash
        '''
        prompt = self.prompts[0]
        packet_id = getPackedIdFromPromptId(prompt)
        data.remove_packet_from(packet_id=packet_id, user_id=self.opener)

        for prompt in self.prompts:
            p = Prompt()
            p.initWithParams(id = prompt, 
                             userIdHex = self.opener, 
                             data = data)

@dataclass
class PromptCreated(Event):
    to: str
    promptId: int
    IPFSCid: int

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''
        Add the IPFS hash to the prompt in the database and the "name" of the prompt
        '''
        prompt = Prompt()
        promptCid = int256ToCid(self.IPFSCid)
        prompt_json = json.loads(IPFSClient.http_client.cat(promptCid).decode("utf-8"))
        name = prompt_json['name']
        rarity = prompt_json['rarity']
        prompt.addIPFSHash(self.promptId, promptCid, name, rarity, data)

@dataclass
class CreateImage(Event):
    creator: str
    cardId: int

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''
        address indexed creator, uint256 prompts
        '''

        image = Image()
        image.initWithParams(id=self.cardId, userIdHex=self.creator)
        image.writeToDb(data)
        image.freezePrompts(data)

@dataclass
class ImageCreated(Event):
    creator: str
    imageId: int
    IPFSCid: int

    def handle(self, contract, provider, IPFSClient, data: Data):
        '''
        address indexed creator, uint256 prompts
        '''
        image = Image()
        imageCid = int256ToCid(self.IPFSCid)
        
        # IPFSClient.download(imageCid, path=f"ipfs/image/{from_int_to_hex_str(self.imageId)}.png")
        ipfs_data = IPFSClient.http_client.get_json(imageCid)

        card_image = Img.fromarray(np.array(json.loads(ipfs_data["image"]), dtype='uint8'))

        card_image.save(f"ipfs/image/{from_int_to_hex_str(self.imageId)}.png")
        
        prompts = ipfs_data["prompts"]

        image.addIPFSHash(self.imageId, imageCid, prompts, data)

@dataclass
class DestroyImage(Event):
    imageId: int
    userId: str

    def handle(self, contract, provider, IPFSClient: ipfs_api, data: Data):
        '''
        address indexed creator, uint256 prompts, string uri
        '''
        # delete the image from the db
        image = data.get_image(self.imageId)
        image.unfreezePrompts(data)
        IPFSClient.unpin(image.hash)
        image.deleteFromDb(data)


@dataclass
class TransferEvent(Event):
    buyer: str
    seller: str
    id: int
    value: int  # value of the NFT

@dataclass
class PacketTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient, data: Data):
        data.transfer_packet(self.id, self.seller, self.buyer, self.value)

@dataclass
class PromptTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient, data: Data):
        data.transfer_prompt(self.id, self.seller, self.buyer, self.value)
        

@dataclass
class CardTransfered(TransferEvent):

    def handle(self, contract, provider, IPFSClient, data: Data):
        data.transfer_image(self.id, self.seller, self.buyer, self.value)


@dataclass 
class UpdateNFT(Event):
    id: int
    isListed: bool
    price: int
    tokenOwner: str

@dataclass
class UpdateListPrompt(UpdateNFT):
    def handle(self, contract, provider, IPFSClient, data: Data):
        if self.isListed:
            data.list_prompt(prompt_id=self.id, price=self.price, token_owner=self.tokenOwner.lower())
        else:
            data.unlist_prompt(self.id ,token_owner=self.tokenOwner.lower())

@dataclass
class UpdateListPacket(UpdateNFT):
    def handle(self, contract, provider, IPFSClient, data: Data):
        if self.isListed:
            data.list_packet(self.id, self.price, token_owner=self.tokenOwner.lower())
        else:
            data.unlist_packet(self.id, token_owner=self.tokenOwner.lower())

@dataclass
class UpdateListImage(UpdateNFT):
    def handle(self, contract, provider, IPFSClient, data: Data):
        if self.isListed:
            data.list_image(self.id, self.price, token_owner=self.tokenOwner.lower())
        else:
            data.unlist_image(self.id, token_owner=self.tokenOwner.lower())



def get_event_class(event_name):
    event_class = globals()[event_name]
    return event_class