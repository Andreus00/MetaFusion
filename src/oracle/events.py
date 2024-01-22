'''
This file contains the events that the oracle can handle.
'''


from dataclasses import dataclass
from abc import abstractmethod, ABC
from typing import List
import os
import json
import io
from PIL import Image
import time

from ..word_generator import Atlas
from ..utils import utils
from ..db.data import Data
from ..word_generator.prompt_builder import Prompt

PACKET_SIZE = 8
word_generator = Atlas.WordExtractor()


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
                                        "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
                                        "nonce": provider.eth.get_transaction_count("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"),
                                    })
            # sign the transaction
            signed_tx = provider.eth.account.sign_transaction(call_func, private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")

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

        # generate the image
        image: Image = model(prompt=prompt).images[0]


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
                                        "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
                                        "nonce": provider.eth.get_transaction_count("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"),
                                    })
        # sign the transaction
        signed_tx = provider.eth.account.sign_transaction(call_func, private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")

        # send the transaction
        send_tx = provider.eth.send_raw_transaction(signed_tx.rawTransaction)

        # wait for transaction receipt
        tx_receipt = provider.eth.wait_for_transaction_receipt(send_tx)

@dataclass
class WillToBuyEvent(Event):
    '''
    Pay the seller and send the NFT to the buyer
    '''
    buyer: str
    seller: str
    id: str
    value: int

    def refund(self, contract, provider):
        '''
        Refund the buyer if something went wrong
        '''

        call_func = contract.functions.refund(**{"buyer": self.buyer,  "value": self.value})\
                            .build_transaction({
                                "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
                                "nonce": provider.eth.get_transaction_count("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"),
                            })
            
        # sign the transaction
        signed_tx = provider.eth.account.sign_transaction(call_func, private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")

        # send the transaction
        send_tx = provider.eth.send_raw_transaction(signed_tx.rawTransaction)

        # wait for transaction receipt
        tx_receipt = provider.eth.wait_for_transaction_receipt(send_tx)
            


@dataclass
class WillToBuyPacket(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, model, data: Data):
        '''
        Pay the seller and send the packet to the buyer
        '''

        packet = data.get_packet(self.id)
        price = packet.price
        is_listed = packet.isListed
        
        # check if the buyer sent enough money
        if is_listed and self.value >= price:
            # execute the transfer

            # call the function
            call_func = contract.functions.transferPacket(**{"buyer": self.buyer, "seller": self.seller, "packetId": self.id, "val": price})\
                            .build_transaction({
                                "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
                                "nonce": provider.eth.get_transaction_count("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"),
                            })
            
            # sign the transaction
            signed_tx = provider.eth.account.sign_transaction(call_func, private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")

            # send the transaction
            send_tx = provider.eth.send_raw_transaction(signed_tx.rawTransaction)

            # wait for transaction receipt
            tx_receipt = provider.eth.wait_for_transaction_receipt(send_tx)
            
        else:
            if not is_listed:
                # the tracker didn't have time to update the DB. 
                # This is an edge case in which list and 
                # buy are very close, but it can happen.
                # In theory the buyer (who acts as an attacker) could spam
                # the network with buy requests to make this happen.
                # We discourage this behaviour by applying a fee
                # to the buyer every time he buys a packet.
                self.refund(contract, provider)
                raise Exception("Packet is not listed in DB whie it should be")
            else:
                # genuine refund
                # refund the buyer
                self.refund(contract, provider)

@dataclass
class WillToBuyPrompt(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, model, data: Data):
        '''
        Pay the seller and send the prompt to the buyer
        '''

        prompt = data.get_prompt(self.id)
        price = prompt.price
        is_listed = prompt.isListed
            
        # check if the buyer sent enough money
        if is_listed and self.value >= price:
            # execute the transfer

            # call the function
            call_func = contract.functions.transferPrompt(**{"buyer": self.buyer, 
                                                             "seller": self.seller, 
                                                             "promptId": self.id, 
                                                             "val": price})\
                            .build_transaction({
                                "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
                                "nonce": provider.eth.get_transaction_count("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"),
                            })
            
            # sign the transaction
            signed_tx = provider.eth.account.sign_transaction(call_func, 
                                                              private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
            
            # send the transaction
            send_tx = provider.eth.send_raw_transaction(signed_tx.rawTransaction)

            # wait for transaction receipt
            tx_receipt = provider.eth.wait_for_transaction_receipt(send_tx)
            
        else:
            if not is_listed:
                # the tracker didn't have time to update the DB. 
                # This is an edge case in which list and 
                # buy are very close, but it can happen.
                # In theory the buyer (who acts as an attacker) could spam
                # the network with buy requests to make this happen.
                # We discourage this behaviour by applying a fee
                # to the buyer every time he buys a prompt.
                self.refund(contract, provider)
                raise Exception("Prompt is not listed in DB whie it should be")
            else:
                # genuine refund
                # refund the buyer
                self.refund(contract, provider)


@dataclass
class WillToBuyImage(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, model, data: Data):
        '''
        Pay the seller and send the packet to the buyer
        '''
        image = data.get_image(self.id)
        price = image.price
        is_listed = image.isListed
            
        # check if the buyer sent enough money
        if is_listed and self.value >= price:
            # execute the transfer
            
            # call the function
            call_func = contract.functions.transferCard(**{"buyer": self.buyer, 
                                                             "seller": self.seller, 
                                                             "imageId": self.id, 
                                                             "val": price})\
                            .build_transaction({
                                "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
                                "nonce": provider.eth.get_transaction_count("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"),
                            })
            
            # sign the transaction
            signed_tx = provider.eth.account.sign_transaction(call_func, 
                                                              private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
            
            # send the transaction
            send_tx = provider.eth.send_raw_transaction(signed_tx.rawTransaction)

            # wait for transaction receipt
            tx_receipt = provider.eth.wait_for_transaction_receipt(send_tx)

        else:
            if not is_listed:
                # the tracker didn't have time to update the DB. 
                # This is an edge case in which list and 
                # buy are very close, but it can happen.
                # In theory the buyer (who acts as an attacker) could spam
                # the network with buy requests to make this happen.
                # We discourage this behaviour by applying a fee
                # to the buyer every time he buys a image.
                self.refund(contract, provider)
                raise Exception("Image is not listed in DB whie it should be")
            else:
                # genuine refund
                # refund the buyer
                self.refund(contract, provider)


def get_event_class(event_name):
    '''
    Get the event class from the event name.
    '''
    event_class = globals()[event_name]
    return event_class