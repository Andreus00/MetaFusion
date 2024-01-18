import web3
import hydra
import asyncio
import logging
import time
import json
from .event_handler import handle_event, initTrackerFilters
import ipfs_api
import os
import multiaddr
from ..db.data import Data

logger = logging.getLogger(__name__)


def instantiateProvider(provider_cfg):
    provider = hydra.utils.instantiate(provider_cfg)

    logger.info("Provider instantiated.")
    is_connected = provider.is_connected()
    if is_connected:
        logger.info(f"Connection test: {provider.is_connected()}")
    else:
        logger.error(f"Connection test: {provider.is_connected()}")
        raise ConnectionError("Connection to provider failed.")
    return provider

def instantiateIPFS(ipfs_cfg):
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
    # open artifacts/contracts/MetafusionPresident.sol/MetafusionPresident.json
    

    logger.info(f"Current working directory: {os.getcwd()}")

    with open("./artifacts/contracts/MetafusionPresident.sol/MetaFusionPresident.json") as f:
        contract_json = json.load(f)
    return contract_json["abi"]

def initContract(contract_cfg, provider):
    ABI = getABI()
    contract = provider.eth.contract(
        # address = contract_cfg.contract_address,
        abi = ABI
    )
    return contract

def initData(contract, filters):
    return Data(create_db=True)


def loop(provider, contract, filters, IPFSClient, data, cfg):
    while True:
        for filter in filters:
            for idx, event in enumerate(filter.get_new_entries()):
                try:
                    handle_event(event, provider, contract, IPFSClient, data, logger)
                except Exception as e:
                    print(f"Error handling event {idx}: {e}")
        time.sleep(cfg.poll_interval)


@hydra.main(config_path="../../conf", config_name="tracker_config")
def main(cfg):
    # connect to IPFS
    IPFSClient = instantiateIPFS(cfg.ipfs)

    # Create web3 connection
    provider = instantiateProvider(cfg.provider)

    contract = initContract(cfg.contract, provider)

    filters = initTrackerFilters(contract)

    data = initData(contract, filters)

    loop(provider, contract, filters, IPFSClient, data, cfg)

if __name__ == "__main__":
    main()
