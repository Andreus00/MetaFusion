'''
Api endpoints for the web api.

Check src/web_api/docs/openapi.yaml for the documentation.
'''

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from src.db.data import Data, Image
from hydra.utils import instantiate
from hydra import initialize, compose
from omegaconf import OmegaConf
import re

with initialize(version_base=None, config_path="../../conf", job_name="web_api"):
    cfg = compose(config_name="webapi_config")
    print(OmegaConf.to_yaml(cfg))

database: Data = instantiate(cfg.db)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def set_response_content_type(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json"
    return response



@app.get('/user/{publicKey}')
async def get_user(publicKey: str):
    '''
    Get all the data of an user.
    '''
    packet, prompt, card, trans = database.get_user(publicKey)
    dataj = {'packets': packet, 'prompts': prompt, 'cards': card, 'transactions': trans}
    return dataj

@app.get("/packet/{packetid}")
async def get_packet(packetid: str, r: Request):
    '''
    Get all the data of a packet.
    '''
    packet = database.get_packet(packetid, as_json=True)
    if packet is None:
        raise HTTPException(404, detail='packet not found')
    return packet

@app.get("/packet/{packetid}/transactions")
async def get_packet_transactions(packetid: str, r: Request):
    '''
    Get all the transactions of a packet.
    '''
    trans  = database.get_token_transfer_events(packetid)
    if trans is None:
        raise HTTPException(404, detail='packet transactions not found')
    return trans

@app.get("/packets/")
async def get_packets(r: Request):
    '''
    Get all the packets.
    '''
    packets = database.get_all_packets(only_listed=True)
    return packets



@app.get("/prompt/{promptid}")
async def get_prompt(promptid: str, r: Request):
    '''
    Get all the data of a prompt.
    '''
    prompt = database.get_prompt(promptid, as_json=True)
    if prompt is None:
        raise HTTPException(404, detail='prompt not found')
    return prompt

@app.get("/prompt/{promptid}/transactions")
async def get_prompt_transactions(promptid: str, r: Request):
    '''
    Get all the transactions of a prompt.
    '''
    prompt = database.get_token_transfer_events(promptid)
    if prompt is None:
        raise HTTPException(404, detail='prompt not found')
    return prompt

@app.get("/prompts/")
async def get_prompts(r: Request):
    '''
    Get all the prompts.
    '''
    prompts = database.get_all_prompts(only_listed=True)
    return prompts

def extract_card_info(card: Image):
    '''
    Extracts the info from an Image class.
    '''
    prompts = []
    for i in range(7):
        prompt = Image.getPrompt(i)
        prompts.append(prompt)
        print(prompt)


@app.get("/card/{cardid}")
async def get_card(cardid: str, r: Request):
    '''
    Get all the data of a card.
    '''
    card = database.get_image(cardid, as_json=True)
    return card

@app.get("/card/{cardid}/transactions")
async def get_card_transactions(cardid: str, r: Request):
    '''
    Get all the transactions of a card.
    '''
    trans = database.get_token_transfer_events(cardid)
    if trans is None:
        raise HTTPException(404, detail='trans not found')
    return trans

@app.get("/card/{cardid}/image")
async def get_card_image(cardid: str, r: Request):
    '''
    Get the image of a card.
    '''
    # first check if the user is not trying to do something malicious
    # by checking if the cardid is in the right format
    if len(cardid) > 66:
        raise HTTPException(404, detail='card not found - length should be 66')
    if not re.match(r'[a-z0-9]', cardid):
        raise HTTPException(404, detail='card not found - wrong format')

    base_url: str = "ipfs/image/"
    card_url = os.path.join(base_url, cardid + ".png")
    print(card_url)
    if os.path.exists(card_url):
        return FileResponse(card_url)
    raise HTTPException(404, detail='card not found')


@app.get("/cards/")
async def get_cards(r: Request):
    '''
    Get all the cards.
    '''
    cards = database.get_all_images(only_listed=True)
    return cards


@app.get("/user/{userId}/name")
async def get_username(userId: str, r: Request):
    '''
    Get the name of a user.
    '''
    name = database.get_username(userId)
    return {"userName": name}

@app.post("/user/{userId}/name")
async def set_username(userId: str, name: str, r: Request):
    '''
    Set the name of a user.
    '''
    database.set_username(userId, name)
    return {"userName": name}



@app.get("/packets/{collectionId}/remaining")
async def get_remainig_number_of_packets(collectionId: int, r: Request):
    '''
    Get the name of a user.
    '''
    num_packets = database.get_remainig_number_of_packets(collectionId)
    return {"remaining": num_packets}



