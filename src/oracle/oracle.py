import web3
from diffusers import AutoPipelineForText2Image
import hydra
import asyncio
import logging
import time
import json

logger = logging.getLogger(__name__)


def instantiateModel(model_cfg):
    model = hydra.utils.call(model_cfg)
    return model


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


def getABI():
    # open artifacts/contracts/MetafusionPresident.sol/MetafusionPresident.json
    import os

    logger.info(f"Current working directory: {os.getcwd()}")

    with open("../../../artifacts/contracts/MetafusionPresident.sol/MetaFusionPresident.json") as f:
        contract_json = json.load(f)
    return contract_json["abi"]

def initContract(contract_cfg, provider):
    ABI = getABI()
    contract = provider.eth.contract(
        # address = contract_cfg.contract_address,
        abi = ABI
    )
    return contract


def initFilter(contract):
    return contract.events.CreateImage.create_filter(fromBlock="latest")

def handle_image_generation(event):
    logger.info(f"New event: {event}")
    pass

def loop(model, provider, contract, filter, cfg):
    while True:
        for event in filter.get_new_entries():
            handle_image_generation(event, model, provider, contract, cfg)
        time.sleep(cfg.poll_interval)




@hydra.main(config_path="../../conf", config_name="oracle_config")
def main(cfg):
    # Instantiate model
    model = None # instantiateModel(cfg.model)
    # Create web3 connection
    provider = instantiateProvider(cfg.provider)

    contract = initContract(cfg.contract, provider)

    filter = initFilter(contract)

    loop(model, provider, contract, filter, cfg)

if __name__ == "__main__":
    main()
