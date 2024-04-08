# MetaFusion - NFT Creation and Exchange Platform

MetaFusion is an innovative decentralized application (DApp) tailored for the creation and exchange of unique digital assets in the form of Non-Fungible Tokens (NFTs). Powered by the Ethereum blockchain and ERC721 protocol, MetaFusion empowers users to unleash their creativity by combining prompts to generate exclusive NFTs.

Check our [technical report](https://github.com/Andreus00/MetaFusion/blob/main/MetaFusion.pdf) for a 360° view of the project.

## Key Features:

- Creative Exploration: Engage in an interactive environment, crafting personalized digital artworks through the combination of prompts.
- Blockchain Security: Utilizing Ethereum ensures a secure, transparent, and tamper-proof ledger for certifying NFT ownership authenticity.
- Community Participation: MetaFusion encourages community involvement, allowing users and investors to actively contribute to the evolution of the NFT ecosystem.
- Transparent Fee Structure: The platform emphasizes fee transparency, with ongoing research to optimize costs for sustainability.

## Project Details:
- Course: Blockchain Exam Project
- Technology Stack: Ethereum blockchain, ERC721 protocol
- Purpose: To provide users with a dynamic and collaborative space for NFT creation and exchange.


## Dependencies
First, you need to have npm installed.

Then you can run
```bash
npm i
```
to install npm dependencies.</br>

Now install Python dependencies. We recommend you to use a Conda environment.
```bash
conda create -n metafusion python?3.9
conda activate metafusion
pip install -r requirements.txt
```

To start the project run the following instructions:

## Hardhat node
To start the hardhat node use:
```shell
npx hardhat node
```

## Deploy the contract
To deploy the contract:
```shell
npx hardhat run scripts/deploy_metafusion.ts --network localhost
```

## Tracker
To start the Tracker use:
```shell
python3 -m src.tracker.tracker
```

## Oracle
To start the Oracle use:
```shell
python3 -m src.oracle.oracle
```


## Webapi server
The web API server exposes some rest API using the Fast API package
install dependencies with following commands:
```shell
python3 -m src.web_api.main
```

## Start the simulation
To start a simulation use:
```shell
npx hardhat run scripts/test_metafusion.ts --network localhost
```
