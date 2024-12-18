'''
Main of the oracle.

run from the root directory with:
python3 -m src.oracle.oracle
'''

import web3
import hydra
import time
import logging
import time
import json
from .events import public_key, private_key
from .event_handler import handle_event, initOracleFilters
import diffusers

import sqlite3
import ipfs_api
import os
import multiaddr
from ..db.data import Data
from ..word_generator import Atlas
import torch
import traceback

logger = logging.getLogger(__name__)


def initModel(model_cfg):
    '''
    Initializes the diffusion model from the config file.
    '''
    model = hydra.utils.call(model_cfg.from_pretrained, torch_dtype=torch.float16)
    model.to(model_cfg.device)
    logger.info("Model instantiated.")
    return model

def instantiateProvider(provider_cfg):
    '''
    Instantiates the web3 provider from the config file.
    '''
    provider: web3.Web3 = hydra.utils.instantiate(provider_cfg)
    provider.eth.default_account = provider.eth.accounts[0]

    logger.info("Provider instantiated.")
    is_connected = provider.is_connected()
    if is_connected:
        logger.info(f"Connection test: {provider.is_connected()}")
    else:
        logger.error(f"Connection test: {provider.is_connected()}")
        raise ConnectionError("Connection to provider failed.")
    return provider

def instantiateIPFS(ipfs_cfg):
    '''
    Instantiates the IPFS client from the config file.
    '''
    client = ipfs_api

    try:
        # check if IPFS is running, wait max 5 seconds in case it is currently starting up
        ipfs_api.wait_till_ipfs_is_running(2)
    except TimeoutError:    # if IPFS isn't runn
        print("IPFS isn't running, trying to run it myself...")
        ipfs_api.try_run_ipfs()  # try to run the IPFS daemon
        if not ipfs_api.is_ipfs_running():   # check if IPFS is running
            raise Exception("Houston, we have a problem here.")
    print("IPFS is running!")
    
    logger.info("IPFS ID: %s", client.my_id()) # print your IPFS peer ID
    return client


def getABI():
    '''
    Returns the ABI of the contract.
    '''

    with open("./artifacts/contracts/MetafusionPresident.sol/MetaFusionPresident.json") as f:
        contract_json = json.load(f)
    return contract_json["abi"]

def initContract(contract_cfg, provider):
    '''
    Initializes the contract.
    '''
    ABI = getABI()
    address = provider.to_checksum_address(contract_cfg.contract_address)
    contract = provider.eth.contract(
        address = address,
        abi = ABI
    )
    return contract

def loop(provider, contract, filters, IPFSClient, model, data, cfg):
    '''
    Main loop of the oracle.
    '''
    while True:
        for filter in filters:
            for idx, event in enumerate(filter.get_new_entries()):
                try:
                    handle_event(event, provider, contract, IPFSClient, model, data, logger)
                except Exception as e:
                    logger.warning(f"Error handling event {idx}: {e}\nWhile handling event: {event}")
                    traceback.print_exc()
        time.sleep(cfg.poll_interval)
        

def initData():
    '''
    Init the database connection.
    '''
    return Data()

@hydra.main(config_path="../../conf", config_name="oracle_config")
def main(cfg):
    # set the public and private keys of the oracle
    public_key = cfg.public_key
    private_key = cfg.private_key
    # create the model
    model = initModel(cfg.model)

    data = initData()

    # connect to IPFS
    IPFSClient = instantiateIPFS(cfg.ipfs)

    # Create web3 connection
    provider = instantiateProvider(cfg.provider)

    # Instantiate the contract
    contract = initContract(cfg.contract, provider)

    # Initialize the filters
    filters = initOracleFilters(contract)

    # Start the loop
    loop(provider, contract, filters, IPFSClient, model, data, cfg)

if __name__ == "__main__":
    main()
