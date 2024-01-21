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

def set_database(db: Data):
    pass

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for returning all responses as JSON
@app.middleware("http")
async def set_response_content_type(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json"
    return response



@app.get('/user/{publicKey}')
async def get_user(publicKey: str):
    packet, prompt, card, trans = database.get_user(publicKey)
    dataj = {'packets': packet, 'prompts': prompt, 'cards': card, 'transactions': trans}
    return dataj

@app.get("/packet/{packetid}")
async def get_packet(packetid: str, r: Request):
    packet = database.get_packet(packetid, as_json=True)
    if packet is None:
        raise HTTPException(404, detail='packet not found')
    return packet

@app.get("/packet/{packetid}/transactions")
async def get_packet_transactions(packetid: str, r: Request):
    trans  = database.get_token_transfer_events(packetid)
    if trans is None:
        raise HTTPException(404, detail='packet transactions not found')
    return trans

@app.get("/packets/")
async def get_packets(r: Request):
    packets = database.get_all_packets(only_listed=True)
    return packets



@app.get("/prompt/{promptid}")
async def get_prompt(promptid: str, r: Request):
    prompt = database.get_prompt(promptid, as_json=True)
    if prompt is None:
        raise HTTPException(404, detail='prompt not found')
    return prompt

@app.get("/prompt/{promptid}/transactions")
async def get_prompt_transactions(promptid: str, r: Request):
    prompt = database.get_token_transfer_events(promptid)
    if prompt is None:
        raise HTTPException(404, detail='prompt not found')
    return prompt

@app.get("/prompts/")
async def get_prompts(r: Request):
    prompts = database.get_all_prompts(only_listed=True)
    return prompts

def extract_card_info(card: Image):
    
    collection = card.getOriginalCollection()
    prompts = []
    for i in range(7):
        prompt = Image.getPrompt(i)
        prompts.append(prompt)
        print(prompt)


@app.get("/card/{cardid}")
async def get_card(cardid: str, r: Request):
    card = database.get_image(cardid, as_json=True)
    return card

    if card is None:
        raise HTTPException(404, detail='card not found')
    return {**card.__dict__, 'prompts': info}

@app.get("/card/{cardid}/transactions")
async def get_card_transactions(cardid: str, r: Request):
    trans = database.get_token_transfer_events(cardid)
    if trans is None:
        raise HTTPException(404, detail='trans not found')
    return trans

@app.get("/card/{cardid}/image")
async def get_card_image(cardid: str, r: Request):

    # first check if the user is not trying to do something malicious
    # by checking if the cardid is in the right format
    if len(cardid) != 66:
        raise HTTPException(404, detail='card not found - length should be 66')
    if not re.match(r'[a-z0-9]{66}', cardid):
        raise HTTPException(404, detail='card not found - wrong format')

    base_url: str = "ipfs/image/"
    card_url = os.path.join(base_url, cardid + ".png")
    print(card_url)
    if os.path.exists(card_url):
        return FileResponse(card_url)
    raise HTTPException(404, detail='card not found')


@app.get("/cards/")
async def get_cards(r: Request):
    cards = database.get_all_images(only_listed=True)
    return cards





