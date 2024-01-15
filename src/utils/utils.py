

def from_int_to_hex_str(integer: int):
    return integer
    return str(hex(integer))

def from_str_hex_to_int_str(hex_string: str):
    return int(hex_string, 0)


def getInfoFromPacketId(packet_id: int) -> (int, int):
    '''
    id int32: cccc cccc cccc cccc pppp pppp pppp pppp
    Return the collection id (c) and the packet number (p).
    '''
    collection = packet_id >> 16
    packet = packet_id & 0xFFFF
    return collection, packet

def getInfoFromPromptId(prompt_id: int) -> (int, int, int, int):
    '''
    id int32: iiic cccc cccc cccc tttp pppp pppp pppp
    Return prompt index (i), the collection id (c), the type id (t) and the packet number (p).
    '''
    index = prompt_id >> 28
    collection = (prompt_id >> 16) & 0x1FFF
    type_id = (prompt_id >> 13) & 0x7
    packet = prompt_id & 0x1FFF
    return index, collection, type_id, packet

def getInfoFromImageId(image_id: int) -> (int, int, int, int, int, int, int):
    '''
    id int256:  ssss ssss ssss ssss ssss ssss ssss ssss
                ssss ssss ssss ssss ssss ssss ssss ssss
                iiic cccc cccc cccc tttp pppp pppp pppp
                iiic cccc cccc cccc tttp pppp pppp pppp
                iiic cccc cccc cccc tttp pppp pppp pppp
                iiic cccc cccc cccc tttp pppp pppp pppp
                iiic cccc cccc cccc tttp pppp pppp pppp
                iiic cccc cccc cccc tttp pppp pppp pppp
    Return the seed (s), and all the six prompts.
    '''
    seed = image_id >> 192
    prompts = []
    for i in range(6):
        prompts.append(image_id >> (i*32) & 0xFFFFFFFF)
    
    return seed, *prompts