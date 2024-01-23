'''
This file contains the events that the oracle can handle.
'''


from dataclasses import dataclass
from abc import abstractmethod, ABC
from typing import List
import os
import json
import io
from torch import Generator
from PIL import Image
import time

from ..word_generator import Atlas
from ..utils import utils
from ..db.data import Data
from ..word_generator.prompt_builder import Prompt

PACKET_SIZE = 8
word_generator = Atlas.WordExtractor()
public_key = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"   # testnet account
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # testnet account


@dataclass
class Event(ABC):
    '''
    Basic class for events.
    '''
    event: str

    @abstractmethod
    def handle(self, contract, provider, IPFSClient, model, data):
        '''
        Handle the event
        '''
        pass

    def log(self, logger):
        '''
        Log the event
        '''
        attributes = "\n".join([f"{k}: {v}" for k, v in self.__dict__.items()])
        msg = f"""
                ====================
                {attributes}
                """
        logger.info(f"{msg}")

@dataclass
class PacketOpened(Event):
    '''
    Handle the opening of a packet.
    '''

    opener: str
    prompts: List[int]

    def handle(self, contract, provider, IPFSClient, model, data):
        '''
        Generate and add prompt on IPFS
        '''
        for prompt in self.prompts:
            _, packet, type_id, collection = utils.getInfoFromPromptId(prompt)

            random_prompt, rarity = word_generator.generate_prompt(collection, type_id, prompt)

            data = {
                "name": random_prompt,
                "id": prompt,
                "collection": collection,
                "type": type_id,
                "rarity": rarity,
            }

            # push the prompt on IPFS
            cid = IPFSClient.http_client.add_bytes(json.dumps(data).encode("utf-8"))

            cid_int = utils.cidToInt256(cid)
            
            # call the contract function to notify the blockchain.
            call_func = contract.functions.promptMinted(**{
                                        "IPFSCid": cid_int,
                                        "promptId": prompt,
                                        "to": self.opener,
                                        })\
                                    .build_transaction({
                                        "from": public_key,
                                        "nonce": provider.eth.get_transaction_count(public_key),
                                    })
            # sign the transaction
            signed_tx = provider.eth.account.sign_transaction(call_func, private_key=private_key)

            # send the transaction
            send_tx = provider.eth.send_raw_transaction(signed_tx.rawTransaction)

            # wait for transaction receipt
            tx_receipt = provider.eth.wait_for_transaction_receipt(send_tx)
                
                

@dataclass
class CreateImage(Event):
    '''
    Handle the creation of an image.
    '''
    creator: str
    cardId: int

    def handle(self, contract, provider, IPFSClient, model, data: Data):
        '''
        Generate and image and add it to IPFS
        '''
        seed, (style_id, eyes_id, color_id, tool_id, hat_id, character_id) = utils.getInfoFromImageId(self.cardId)

        # read the names from the db
        character = data.get_prompt(character_id)
        hat = data.get_prompt(hat_id)
        tool = data.get_prompt(tool_id)
        color = data.get_prompt(color_id)
        eyes = data.get_prompt(eyes_id)
        style = data.get_prompt(style_id)

        # generate the prompt
        prompt = Prompt().set_character(character)\
                    .set_hat(hat)\
                    .set_tool(tool)\
                    .set_color(color)\
                    .set_eyes(eyes)\
                    .set_style(style)\
                    .build()
        
        # instantiate the generator
        generator = Generator().manual_seed(seed)

        # generate the image
        image: Image = model(prompt=prompt, generator=generator).images[0]
        
        # save the image in a buffer
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte = img_byte_arr.getvalue()

        # push the image on IPFS
        cid = IPFSClient.http_client.add_bytes(img_byte)

        img_byte_arr.flush()
        img_byte_arr.close()

        # publish the cid on the blockchain
        cid_int = utils.cidToInt256(cid)

        call_func = contract.functions.imageMinted(**{
                                        "IPFSCid": cid_int,
                                        "imageId": self.cardId,
                                        "to": self.creator, 
                                        })\
                                    .build_transaction({
                                        "from": public_key,
                                        "nonce": provider.eth.get_transaction_count(public_key),
                                    })
        # sign the transaction
        signed_tx = provider.eth.account.sign_transaction(call_func, private_key=private_key)

        # send the transaction
        send_tx = provider.eth.send_raw_transaction(signed_tx.rawTransaction)

        # wait for transaction receipt
        tx_receipt = provider.eth.wait_for_transaction_receipt(send_tx)


def get_event_class(event_name):
    '''
    Get the event class from the event name.
    '''
    event_class = globals()[event_name]
    return event_class