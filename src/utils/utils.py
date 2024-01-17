import base58
from typing import List

def cidToInt256(cid):
    return int.from_bytes(base58.b58decode(cid)[2:], "big")

def int256ToCid(int256):
    return base58.b58encode(b"\x12\x20" + int.to_bytes(int256, 32, "big")).decode("utf-8")
    

def from_int_to_hex_str(integer: int):
    return str(hex(integer))

def from_str_hex_to_int_str(hex_string: str):
    return int(hex_string, 16)


def getInfoFromPacketId(packet_id: int) -> (int, int):
    '''
    id int32: pppp pppp pppp pppp cccc cccc cccc cccc
    Return the collection id (c) and the packet number (p).
    '''
    packet = packet_id >> 16
    collection = packet_id & 0xFFFF
    return packet, collection

def getInfoFromPromptId(prompt_id: int) -> (int, int, int, int):
    '''
    id int32: iiip pppp pppp pppp tttc cccc cccc cccc
    Return prompt index (i), the collection id (c), the type id (t) and the packet number (p).
    '''
    index = prompt_id >> 28
    packet = (prompt_id >> 16) & 0x1FFF
    type_id = (prompt_id >> 13) & 0x7
    collection = prompt_id & 0x1FFF
    return index, packet, type_id, collection

def getPackedIdFromPromptId(prompt_id: int) -> int:
    return prompt_id & 0x1fff1fff

def getInfoFromImageId(image_id: int) -> (int, List[int]):
    '''
    id int256:  iiip pppp pppp pppp tttc cccc cccc cccc
                iiip pppp pppp pppp tttc cccc cccc cccc
                iiip pppp pppp pppp tttc cccc cccc cccc
                iiip pppp pppp pppp tttc cccc cccc cccc
                iiip pppp pppp pppp tttc cccc cccc cccc
                iiip pppp pppp pppp tttc cccc cccc cccc
                ssss ssss ssss ssss ssss ssss ssss ssss
                ssss ssss ssss ssss ssss ssss ssss ssss
    Return the seed (s), and all the six prompts.
    '''
    seed = image_id & 0xffffffffffffffff
    prompts = []
    image_id = image_id >> 64
    for _ in range(6):
        prompts.append(image_id & 0xFFFFFFFF)
        image_id = image_id >> 32
    
    return seed, prompts