import { ethers } from "hardhat";
import { TransactionReceipt } from "@ethersproject/abstract-provider";

// import * as fs from 'fs';

const contract_address = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

const owner_priv_key: string = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'

const other_priv_key: string = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
const other2_priv_key: string = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'

const collections = [1, 2]

var packets: { [user: string] : { [collection: number] : number[]} } = {};
packets[owner_priv_key] = {};
packets[other_priv_key] = {};
packets[other2_priv_key] = {};

var prompts: { [user: string] : { [collection: number] : number[]} } = {};
prompts[owner_priv_key] = {};
prompts[other_priv_key] = {};
prompts[other2_priv_key] = {};

var images: {[user: string] : {[collections: number] : number[]}} = {}
images[owner_priv_key] = {};
images[other_priv_key] = {};
images[other2_priv_key] = {};

const FORGE_TOT_PACKETS = 3;
const NUM_PROMPT_PER_IMAGE = 6;

function genPKUUID(collection: number , idInCollection: number){
    return ((idInCollection) << (16)) | (collection)
}

async function connect(contractName: string) {

    const SIMULATE_PACKET_FORGE = true;
    const SIMULATE_PACKET_TRANSFER = true;
    const SIMULATE_PACKET_OPENING = true;
    const SIMULATE_IMAGE_CREATION = false;


    const wallet_owner = await ethers.getSigner(owner_priv_key);
    
    const wallet_other = await ethers.getSigner(other_priv_key);

    const wallet_other2 = await ethers.getSigner(other2_priv_key);
    console.log('wallet_other: ', wallet_other.address);

    // connect to contract as owner and forge collection

    let args = { value: ethers.parseEther("1") }

    const contract_owner = await ethers.getContractAt(contractName, contract_address, wallet_owner)
    const contract_other = await ethers.getContractAt(contractName, contract_address, wallet_other)
    const contract_other_2 = await ethers.getContractAt(contractName, contract_address, wallet_other2)

    const contracts = [contract_other, contract_other_2]

    if (SIMULATE_PACKET_FORGE) {
        for (let i = 0; i < collections.length; i++) {
            let collection = collections[i]
            let tx = await contract_owner.forgeCollection(collection)
            await tx.wait();

            for (let x = 0; x < contracts.length; x++) {
                let cur_contract = contracts[x];
                let cur_address: string = await cur_contract.runner?.getAddress();  // it actually exists
                console.log(cur_address);
                packets[cur_address][collection] = [];
                console.log(packets);
            }

            let tot_packets = 0;
            for (let j = 0; j < contracts.length; j++) {
                let cur_contract = contracts[j];
                let cur_address: string = await cur_contract.runner?.getAddress();  // it actually exists

                for (let k = 0; k < FORGE_TOT_PACKETS; k++) {
                    tot_packets++;
                    let packID = genPKUUID(collection, tot_packets)
                    let tx = await cur_contract.forgePacket(collection, args)
                    await tx.wait();
                    packets[cur_address][collection].push(packID);
                }
            }
        }

        console.log(images);
    }

    // sleep
    await new Promise(r => setTimeout(r, 2500));

    if (SIMULATE_PACKET_TRANSFER) {
        let seller = wallet_other;
        let contract_seller = contract_other;
        let buyer = wallet_other2;
        let contract_buyer = contract_other_2;

        // seller lists packet for sale
        let packet_id = packets[seller.address][collections[0]][0];

        let tx = await contract_seller.listPacket(packet_id);
        await tx.wait();

        // buyer calls the willToBuy
        let tx2 = await contract_buyer.buyPacket(packet_id, args);
        await tx2.wait();

        // wait for the transfer to be completed
        await new Promise(r => setTimeout(r, 2500));

        packets[seller.address][collections[0]].splice(0, 1);
        packets[buyer.address][collections[0]].push(packet_id);

        // check the ownership on blockchain
        let owner = await contract_seller.ownerOfPacket(packet_id);
        console.log('new owner: ', owner);

        // check the balance of the buyer and seller
        let balance_other = await seller.provider.getBalance(other_priv_key);
        console.log('balance_other: ', balance_other);

        let balance_other_2 = await buyer.provider.getBalance(other2_priv_key);
        console.log('balance_other_2: ', balance_other_2);
    }


    if (SIMULATE_PACKET_OPENING) {
        // cycle on collections, wallets  and packets
        for (let i = 0; i < collections.length; i++) {
            let collection = collections[i];
            for (let j = 0; j < contracts.length; j++) {
                let cur_contract = contracts[j];
                let cur_address = await cur_contract.runner?.getAddress();
                let cur_packets = packets[cur_address][collection];
                for (let k = 0; k < cur_packets.length; k++) {
                    let packet_id =cur_packets[k];
                    let args = { value: ethers.parseEther("0.01") }
                    let tx = await cur_contract.openPacket(packet_id, args);
                    let rc = await tx.wait();
                    let event = rc.logs[rc.logs.length - 1];
                    const [sender, prs, uris] = event.args;
                    for (let l = 0; l < prs.length; l++) {
                        prompts[cur_address][collection] = prs[l];
                    }
                }
            }
        }
        console.log(prompts);
    }

    if (SIMULATE_IMAGE_CREATION){
        let collection = collections[0];
        images[other_priv_key][collection] = []; // create list 

        let myPrompts = prompts[other_priv_key][collection];

        let usePrompts = [0, 0, 0, 0, 0, 0];
        for (let i = 0; i < NUM_PROMPT_PER_IMAGE; i++) {
          let promptId = myPrompts[i];
          let promptType = ((promptId >> 13) & 0x7);
          usePrompts[promptType] = promptId;
        }
        
        let tx = await contract_other.createImage(usePrompts)
        let rc = await tx.wait();
        let event = rc.logs[rc.logs.length - 1];
        const [sender, cardId, uri] = event.args;
        let cur_address = await contract_other.runner?.getAddress();
        images[cur_address][collection].push(cardId);

    }


    return;

}


async function main() {

    const contract = await connect("MetaFusionPresident");

    console.log(
        'mintPacket completed.');
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});

/*
import { ethers } from "hardhat";
import * as fs from 'fs';

async function getContract(contractName: string, address: string) {
    // connect to contract
    var contract = await ethers.getContractAt(contractName, "0x5fbdb2315678afecb367f032d93f642f64180aa3");
    return contract;
}
async function connectAccount(contract: any, address: string) {
    // login with private key
    const wallet = new ethers.Wallet(address);
    // connect to network
    const connectedContract = await contract.connect(wallet);
    return connectedContract;

}
async function main() {
    const contractName = "MetaFusionPresident";
    const contractAddress = "0x5fbdb2315678afecb367f032d93f642f64180aa3";

    const ownerPrivateKey = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    const otherPrivateKey = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'

    const contract = await getContract(contractName, contractAddress);

    const connectedContractOwner = await connectAccount(contract, ownerPrivateKey);
    const connectedContractOther = await connectAccount(contract, otherPrivateKey);

    for (let i = 2; i <= 100; i++) {
		console.log("Creating collection " + i);
        let tx = await connectedContractOwner.forgeCollection(i);
        await tx.wait();
        for (let j = 1; j <= 100; j++) {
			console.log("Forging packet " + j +  " for collection " + i);
            let tx = await connectedContractOther.forgePacket(i);
            await tx.wait();
        }
    }

    console.log(
        'mintPacket completed.');
}
*/