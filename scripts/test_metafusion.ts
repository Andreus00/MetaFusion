import { ethers } from "hardhat";
import { TransactionReceipt } from "@ethersproject/abstract-provider";

// import * as fs from 'fs';

const contract_address = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

const owner_priv_key: string = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'

const other_priv_key: string = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
const other2_priv_key: string = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'

const keys = [other_priv_key, other2_priv_key]

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

const FORGE_TOT_PACKETS = 6;
const NUM_PROMPT_PER_IMAGE = 6;
const NUM_PACKET_TRANSFERS = 6;
const NUM_PROMPT_TRANSFERS = 12;
const NUM_IMAGE_TRANSFERS = 6;

function genPKUUID(collection: number , idInCollection: number){
    return ((idInCollection) << (16)) | (collection)
}

async function connect(contractName: string) {

    const SIMULATE_PACKET_FORGE = true;
    const SIMULATE_PACKET_TRANSFER = true;
    const SIMULATE_PACKET_OPENING = true;
    const SIMULATE_PROMPT_TRANSFER = true;
    const SIMULATE_IMAGE_CREATION = true;
    const SIMULATE_IMAGE_TRANSFER = true;


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

        var seller = wallet_other;
        var contract_seller = contract_other;
        var buyer = wallet_other2;
        var contract_buyer = contract_other_2;

        for (let i = 0; i < NUM_PACKET_TRANSFERS; i++) {

            if (i % 2 == 0) {
                seller = wallet_other;
                contract_seller = contract_other;
                buyer = wallet_other2;
                contract_buyer = contract_other_2;
            }
            else {
                seller = wallet_other2;
                contract_seller = contract_other_2;
                buyer = wallet_other;
                contract_buyer = contract_other;
            }

            // seller lists packet for sale
            let collection = collections[(collections.length - 1) % (i + 1)];
            let packet_id = packets[seller.address][collection][i];

            let tx = await contract_seller.listPacket(packet_id, ethers.parseEther("0.1"));
            await tx.wait();

            // buyer calls the willToBuy
            let tx2 = await contract_buyer.buyPacket(packet_id, args);
            await tx2.wait();

            // wait for the transfer to be completed
            await new Promise(r => setTimeout(r, 2500));

            packets[seller.address][collection].splice(i, 1);
            packets[buyer.address][collection].push(packet_id);

            // check the ownership on blockchain
            let owner = await contract_seller.ownerOfPacket(packet_id);
            console.log('new owner: ', owner);

            // check the balance of the buyer and seller
            let balance_other = await seller.provider.getBalance(other_priv_key);
            console.log('balance_other: ', balance_other);

            let balance_other_2 = await buyer.provider.getBalance(other2_priv_key);
            console.log('balance_other_2: ', balance_other_2);
        }
    }


    if (SIMULATE_PACKET_OPENING) {
        // cycle on collections, wallets  and packets
        for (let i = 0; i < collections.length; i++) {
            let collection = collections[i];
            for (let j = 0; j < contracts.length; j++) {
                let cur_contract = contracts[j];
                let cur_address = await cur_contract.runner?.getAddress();
                let cur_packets = packets[cur_address][collection];
                prompts[cur_address][collection] = [];
                for (let k = 0; k < cur_packets.length; k++) {
                    let packet_id =cur_packets[k];
                    let args = { value: ethers.parseEther("0.01") }
                    let tx = await cur_contract.openPacket(packet_id, args);
                    let rc = await tx.wait();
                    let event = rc.logs[rc.logs.length - 1];
                    const [sender, prs, uris] = event.args;
                    for (let l = 0; l < prs.length; l++) {
                        prompts[cur_address][collection].push(Number(prs[l]));
                    }
                }
            }
        }
        console.log(prompts);

        await new Promise(r => setTimeout(r, 10000));
    }

    function getRandomInt(max: number) {
        return Math.floor(Math.random() * max);
    }

    if (SIMULATE_PROMPT_TRANSFER) {
        var seller = wallet_other;
        var contract_seller = contract_other;
        var buyer = wallet_other2;
        var contract_buyer = contract_other_2;

        for (let i = 0; i < NUM_PROMPT_TRANSFERS; i++) {

            if (i % 2 == 0) {
                seller = wallet_other;
                contract_seller = contract_other;
                buyer = wallet_other2;
                contract_buyer = contract_other_2;
            }
            else {
                seller = wallet_other2;
                contract_seller = contract_other_2;
                buyer = wallet_other;
                contract_buyer = contract_other;
            }

            let collection = collections[(collections.length - 1) % (i + 1)];
            let prompt_id = prompts[seller.address][collection][i];

            let tx = await contract_seller.listPrompt(prompt_id, ethers.parseEther("0.01"));
            await tx.wait();

            let tx2 = await contract_buyer.buyPrompt(prompt_id, args);
            await tx2.wait();

            await new Promise(r => setTimeout(r, 2500));
            prompts[seller.address][collection].splice(i, 1);
            prompts[buyer.address][collection].push(prompt_id);

            // check the ownership on blockchain
            let owner = await contract_seller.ownerOfPrompt(prompt_id);
            console.log('new owner: ', owner);

            // check the balance of the buyer and seller
            let balance_seller = await seller.provider.getBalance(other_priv_key);
            console.log('balance_seller: ', balance_seller);

            let balance_buyer = await buyer.provider.getBalance(other2_priv_key);
            console.log('balance_buyer: ', balance_buyer);
        }
    }

    if (SIMULATE_IMAGE_CREATION){
        console.log("Creating images");

        const TOT_IMAGES: number = 8;   // try to create 8 images. Random users, random collections. 
                                        // If the user does not have characters in the collection, skip the image creation.

        var freezed_prompts = new Set();
        for (let c = 0; c < TOT_IMAGES; c++) {
            let cur_collection = collections[getRandomInt(collections.length)];
            let cur_user = getRandomInt(contracts.length);
            let cur_key = keys[cur_user];
            let cur_contract = contracts[cur_user];
            if (images[cur_key][cur_collection] == undefined) {
                images[cur_key][cur_collection] = [];
            }
            console.log(cur_key, cur_collection, cur_user);
            let myPrompts = prompts[cur_key][cur_collection];
            let usePrompts = [0, 0, 0, 0, 0, 0];
            for (let i = 0; i < myPrompts.length; i++) {
                if (freezed_prompts.has(myPrompts[i])) {
                    continue;
                }
                let promptId = myPrompts[i];
                let promptType = ((promptId >> 13) & 0x7);
                usePrompts[promptType] = promptId;
            }
            
            if (usePrompts[0] == 0) {
                continue;
            }

            for (let i = 0; i < usePrompts.length; i++) {
                freezed_prompts.add(usePrompts[i]);
            }
            console.log(usePrompts, cur_key, cur_collection);
            
            let tx = await cur_contract.createImage(usePrompts, { value: ethers.parseEther("0.1") })
            let rc = await tx.wait();
            let event = rc.logs[rc.logs.length - 1];
            const [sender, cardId, uri] = event.args;
            images[cur_key][cur_collection].push(cardId);
        }


    }
    const readline = require('node:readline');
    const { stdin: input, stdout: output } = require('node:process');

    const rl = readline.createInterface({ input, output });

    let final_answer = undefined;

    rl.question('Press [ENTER] to continue execution...', (answer: string) => {
        // TODO: Log the answer in a database
        console.log(`Execution resumed.`);
        final_answer = answer;
        rl.close();
    });

    while (final_answer === undefined) {
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    if(SIMULATE_IMAGE_TRANSFER){
        let seller = wallet_other;
        let contract_seller = contract_other;
        let buyer = wallet_other2;
        let contract_buyer = contract_other_2;

        let collection = collections[0];
        let image_id = images[seller.address][collection][0];
        console.log(images);
        let tx = await contract_seller.listCard(image_id, ethers.parseEther('2.0'));
        await tx.wait();

        tx = await contract_buyer.buyCard(image_id, { value: ethers.parseEther('2.0')});
        await tx.wait();


        await new Promise(r => setTimeout(r, 5500));

        images[seller.address][collection].splice(0, 1);
        images[buyer.address][collection].push(image_id);

        // check the ownership on blockchain
        let owner = await contract_seller.ownerOfCard(image_id);
        console.log('new owner: ', owner);

        // check the balance of the buyer and seller
        let balance_seller = await seller.provider.getBalance(other_priv_key);
        console.log('balance_seller: ', balance_seller);

        let balance_buyer = await buyer.provider.getBalance(other2_priv_key);
        console.log('balance_buyer: ', balance_buyer);
        
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