from typing import Dict, List, Tuple
import sqlite3
import base58
import json


class Packet:

    def initWithParams(self):
        self.id: int = 0
        self.isListed: bool = False
        self.price: int = 0.0

    def fromJson(self, data):
        self.__dict__ = json.loads(data)
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

class Prompt:
    
    def initWithParams(self, id: int, hash: int, URI: str, isListed: bool = False, price: float = 0.0, isFreezed: bool = False):
        self.id: int = id
        self.hash: str = hash   # IPFS hash
        self.isListed: bool = isListed
        self.price: int = price
        self.isFreezed: bool = isFreezed
    
    
    
    def fromJson(self, data):
        self.__dict__ = json.loads(data)
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

class Image:
    id: int
    hash: str   # IPFS hash
    isListed: bool
    price: int
    
    def fromJson(self, data):
        self.__dict__ = json.loads(data)
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
    


class Data:
    def __init__(self):
        con = sqlite3.connect("tracker.db")
        cur = con.cursor()
        # cur.execute("CREATE TABLE IF NOT EXIST Users(addr BIGINT PRIMARY KEY);")
        cur.execute("CREATE TABLE IF NOT EXIST Packets(id BIGINT PRIMARY KEY, isListed BIT DEFAULT 0, price INT DEFAULT 0, userHex VARCHAR(65) NOT NULL);")
        cur.execute("CREATE TABLE IF NOT EXIST Prompts(id BIGINT PRIMARY KEY, ipfsHash VARCHAR(35) NOT NULL, isListed BIT DEFAULT 0, price INT DEFAULT 0, BIT isFreezed DEFAULT 0, userHex VARCHAR(65) NOT NULL);")
        cur.execute("CREATE TABLE IF NOT EXIST Images(id BIGINT PRIMARY KEY, ipfsHash VARCHAR(35) NOT NULL, isListed BIT DEFAULT 0, price INT DEFAULT 0, userHex VARCHAR(65) NOT NULL);")
        cur.execute("CREATE TABLE IF NOT EXIST SellEvent(id INTEGER PRIMARY KEY AUTOINCREMENT, userFromHex VARCHAR(65) NOT NULL, userToHex VARCHAR(65) NOT NULL, price INT DEFAULT 0, type TINYINT CHECK(type IN (0, 1, 2)));") # 0 = Packet, 1 = Prompts, 2 = Images
        cur.execute("CREATE UNIQUE INDEX IF NOT EXIST userPacketsIndex ON Packets(userHex);")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXIST userPromptsIndex ON Prompts(userHex);")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXIST userImagesIndex ON Images(userHex);")
        self.cur = cur

    user_to_packets: Dict[int, List[int]] = {}
    user_to_prompts: Dict[int, List[int]] = {}
    user_to_images: Dict[int, List[int]] = {}

    packets: Dict[int, Packet] = {}
    prompts: Dict[int, Prompt] = {}
    images: Dict[int, Image] = {}

    def get_packets_id_of(self, user_id: int):
        return self.user_to_packets.get(user_id, [])
    
    def get_prompts_id_of(self, user_id: int):
        return self.user_to_prompts.get(user_id, [])
    
    def get_images_id_of(self, user_id: int):
        return self.user_to_images.get(user_id, [])
        

    def get_packet(self, packet_id: int):
        return self.packets.get(packet_id, None)
    
    def get_prompt(self, prompt_id: int):
        return self.prompts.get(prompt_id, None)
    
    def get_image(self, image_id: int):
        return self.images.get(image_id, None)
    
    
    def is_packet_listed(self, packet_id: int):
        return self.packets[packet_id].isListed
    
    def is_prompt_listed(self, prompt_id: int):
        return self.prompts[prompt_id].isListed
    
    def is_image_listed(self, image_id: int):
        return self.images[image_id].isListed
    

    def get_all_packets(self):
        return self.packets.values()
    
    def get_all_prompts(self):
        return self.prompts.values()
    
    def get_all_images(self):
        return self.images.values()
    

    def list_packet(self, packet_id: int):
        self.packets[packet_id].isListed = True
    
    def list_prompt(self, prompt_id: int):
        self.prompts[prompt_id].isListed = True

    def list_image(self, image_id: int):
        self.images[image_id].isListed = True


    def unlist_prompt(self, prompt_id: int):
        self.prompts[prompt_id].isListed = False

    def unlist_image(self, image_id: int):
        self.images[image_id].isListed = False

    def unlist_packet(self, packet_id: int):
        self.packets[packet_id].isListed = False
    
    
    def add_packet_to(self, packet: Packet, user_id: int):
        self.user_to_packets[user_id].append(packet.id)
        self.packets[packet.id] = packet

    def add_prompt_to(self, prompt: Prompt, user_id: int):
        self.user_to_prompts[user_id].append(prompt.id)
        self.prompts[prompt.id] = prompt

    def add_image_to(self, image: Image, user_id: int):
        self.user_to_images[user_id].append(image.id)
        self.images[image.id] = image

    
    def remove_packet_from(self, packet_id: int, user_id: int):
        self.user_to_packets[user_id].remove(packet_id)
        del self.packets[packet_id]

    def remove_prompt_from(self, prompt_id: int, user_id: int):
        self.user_to_prompts[user_id].remove(prompt_id)
        del self.prompts[prompt_id]

    def remove_image_from(self, image_id: int, user_id: int):
        self.user_to_images[user_id].remove(image_id)
        del self.images[image_id]

    
    def transfer_packet(self, packet_id: int, from_user_id: int, to_user_id: int):
        packet = self.get_packet(packet_id)
        self.remove_packet_from(packet_id, from_user_id)
        self.add_packet_to(packet, to_user_id)

    def transfer_prompt(self, prompt_id: int, from_user_id: int, to_user_id: int):
        prompt = self.get_prompt(prompt_id)
        self.remove_prompt_from(prompt_id, from_user_id)
        self.add_prompt_to(prompt, to_user_id)

    def transfer_image(self, image_id: int, from_user_id: int, to_user_id: int):
        image = self.get_image(image_id)
        self.remove_image_from(image_id, from_user_id)
        self.add_image_to(image, to_user_id)


    user_to_packets: Dict[int, List[int]] = {}
    user_to_prompts: Dict[int, List[int]] = {}
    user_to_images: Dict[int, List[int]] = {}

    packets: Dict[int, Packet] = {}
    prompts: Dict[int, Prompt] = {}
    images: Dict[int, Image] = {}

        
    def fromJson(self, data):
        obj = json.loads(data)
        for k, v in obj:
            if(k.startswith("user_to_")):
                self.__dict__[k] = v
            else:
                o = {}
                for k1, v1 in v:
                    obj = None
                    if("packet" in k):
                        obj = Packet()
                    elif("prompt" in k):
                        obj = Prompt()
                    elif("image" in k):
                        obj = Image()
                    if(obj != None):
                        obj.__dict__ = v1
                        o[k1] = obj
                self.__dict__[k] = o
    def toJson(self):
        data = {k: (v if k.startswith("user_to_") else {k1: v1.__dict__ for k1, v1 in v}) for k, v in self.__dict__}
        return json.dumps(data, sort_keys=True)