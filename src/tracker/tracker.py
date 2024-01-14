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
from .data import Data

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
    
    hashed_gattino = ipfs_api.http_client.add("gattino.txt")['Hash']
    logger.info("IPFS API is working, hash: %s", hashed_gattino)

    #Dovrebbe essere quello qua sotto
    # ok però non hashed è un int? come fa a connettersi? credo che python ritorni una stringa o un oggetto bytes (Ma credo più una stringa)
    # tutti possono connettersi e s/caricare merda? Si, possono, MA per ora stiamo usando un nodo privato sul pc di andrea. Se fosse in prod, si, avendo l'hash
    # col nodo sul pc di andrea solo noi possiamo, VIENIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
    # ok, vieni!
    gattino = ipfs_api.http_client.get(hashed_gattino)  # test if the IPFS API is working
    print(gattino)

    logger.info("IPFS API is working, data: %s", gattino)

    # QmeWEMWZfsSRYF427FPwcprrkLydQi5JNxthHHRGjt638e
    # QmWhEKScDyscbRn3eQGh2B4yGbqqeNMZsCw7zDZzSUTaST

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
    return Data()


def loop(provider, contract, filters, IPFSClient, data, cfg):
    num_events_found = 0
    while True:
        for filter in filters:
            for event in filter.get_new_entries():
                handle_event(event, provider, contract, IPFSClient, data)
                num_events_found += 1
        time.sleep(cfg.poll_interval)
        logger.info(f"Events found: {num_events_found}")


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
