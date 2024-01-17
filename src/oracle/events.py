from dataclasses import dataclass
from abc import abstractmethod, ABC
from typing import List
from ..word_generator import Atlas
from ..utils import utils
import os
import json
import io
from PIL import Image

PACKET_SIZE = 8
word_generator = Atlas.WordExtractor()


@dataclass
class Event(ABC):
    event: str

    @abstractmethod
    def handle(self, contract, provider, IPFSClient, model, con):
        pass
        

@dataclass
class PacketOpened(Event):
    opener: str
    prompts: List[int]
    uri: List[str]  # uri of prompts

    def handle(self, contract, provider, IPFSClient, model, con):
        '''
        Generate and add prompt on IPFS
        '''
        for prompt, uri in zip(self.prompts, self.uri):
            _, packet, type_id, collection = utils.getInfoFromPromptId(prompt)

            print(hex(int(prompt)), collection, type_id, packet)

            random_prompt = word_generator.generate_prompt(collection, type_id, prompt)

            #file_name = f"{prompt}.json"
            #path = f"ipfs/prompt/{file_name}"
            #with open(path, "w+") as f:
            data = {
                "name": random_prompt,
                "id": prompt,
                "uri": uri,
                "collection": collection,
                "type": type_id,
            }
            #    json.dump(data, f)

            # push the prompt on IPFS
            cid = IPFSClient.http_client.add_bytes(json.dumps(data).encode("utf-8"))
            #cid = IPFSClient.publish(path)

            cid_int = utils.cidToInt256(cid)

            print("------------------")
            print("Prompt:", prompt)
            print("Name:", random_prompt)
            print("CID:", cid)
            print("CID_int:", cid_int)
            
            # call the function
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
    creator: str
    card: int
    uri: str

    def handle(self, contract, provider, IPFSClient, model, con):
        '''
        Generate and image and add it to IPFS
        '''
        seed, character_id, hat_id, tool_id, color_id, eyes_id, style_id = utils.getInfoFromImageId(self.card)

        with open(f"ipfs/prompt/{character_id}.json") as f:
            character = json.load(f)["name"]
        with open(f"ipfs/prompt/{hat_id}.json") as f:
            hat = json.load(f)["name"]
        with open(f"ipfs/prompt/{tool_id}.json") as f:
            tool = json.load(f)["name"]
        with open(f"ipfs/prompt/{color_id}.json") as f:
            color = json.load(f)["name"]
        with open(f"ipfs/prompt/{eyes_id}.json") as f:
            eyes = json.load(f)["name"]
        with open(f"ipfs/prompt/{style_id}.json") as f:
            style = json.load(f)["name"]

        prompt = f"a 3d {character} with {hat}, {color}, {tool} in his hand, {eyes}, upper bust, {style}, 4k, frontal view"

        image: Image = model(prompt=prompt).images[0]
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte = img_byte_arr.getvalue()
        try:
            # push the image on IPFS
            cid = IPFSClient.http_client.add_bytes(img_byte)
        except Exception as e:
            print(e)
        finally:
            img_byte_arr.flush()
            img_byte_arr.close()

        # publish the cid on the blockchain
        contract.imageMinted(cid, self.card, self.creator)

@dataclass
class WillToBuyEvent(Event):
    '''
    Pay the seller and send the NFT to the buyer
    '''
    buyer: str
    seller: str
    id: str
    value: int


@dataclass
class WillToBuyPacket(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, model, con):
        '''
        Pay the seller and send the packet to the buyer
        '''
        cur = con.cursor()
        try:
            # get the packet price
            print(self.id)
            cur.execute(f"SELECT price FROM packets WHERE id=?", (utils.from_int_to_hex_str(self.id),))
            price = cur.fetchone()[0]
            print(price)
            
            # check if the buyer sent enough money
            if self.value >= price:
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
                
                
                # contract.transferPacket(self.buyer, self.seller, self.id, price)
            else:
                # refund the buyer
                contract.refund(self.buyer, self.value)
        finally:
            cur.close()

@dataclass
class WillToBuyPrompt(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, model, con):
        '''
        Pay the seller and send the packet to the buyer
        '''
        cur = con.cursor()
        try:

            # get the packet price
            cur.execute(f"SELECT price FROM prompts WHERE id={self.id}")
            price = cur.fetchone()[0]
            
            # check if the buyer sent enough money
            if self.value >= price:
                # execute the transfer
                contract.transferPrompt(self.buyer, self.seller, self.id, price)
            else:
                # refund the buyer
                contract.refund(self.buyer, self.value)
        finally:
            cur.close()


@dataclass
class WillToBuyImage(WillToBuyEvent):
    
    def handle(self, contract, provider, IPFSClient, model, con):
        '''
        Pay the seller and send the packet to the buyer
        '''
        cur = con.cursor()
        try:

            # get the packet price
            cur.execute(f"SELECT price FROM images WHERE id={self.id}")
            price = cur.fetchone()[0]
            
            # check if the buyer sent enough money
            if self.value >= price:
                # execute the transfer
                contract.transferImage(self.buyer, self.seller, self.id, price)
            else:
                # refund the buyer
                contract.refund(self.buyer, self.value)
        finally:
            cur.close()


def get_event_class(event_name):
    event_class = globals()[event_name]
    return event_class