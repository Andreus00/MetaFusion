import { ethers } from "hardhat";
import { Contract } from "ethers";


///////////// CONSTANTS ///////////////

var PACKET_COST = "0.1";
var PACKET_OPENING_FEES = "0.01";
var GENERATION_FEES = "0.1";  // The cost of generating an image
var DESTRUCTION_FEES = "0.001";  // The fees for image destruction
var TRANSACTION_FEES = "0.01";  // The fees for the transaction

var NUM_PROMPT_TYPES = 6;  // The number of different prompt types
var PACKET_SIZE = 8;  // The number of different prompt types

///////////// FUNCTIONS ///////////////

async function getAddressFromContract(contract: Contract){
    return await (contract.runner as any)?.getAddress();    // workaround to avoid type error.
}
  
async function forgeCollection(contract: Contract, collection: number){
    let tx = await contract.forgeCollection(collection);
    await tx.wait();
    return tx;
}
  
async function forgePacket(contract: Contract, collection: number, fees: string = PACKET_COST){
    let tx = await contract.forgePacket(collection, {value: ethers.parseEther(fees)});
    await tx.wait();
    return tx;
}
  
async function listPacket(contract: Contract, packetId: number, price: string){
    let tx = await contract.listPacket(packetId, ethers.parseEther(price));
    await tx.wait();
    return tx;
}
  
async function buyPacket(contract: Contract, packetId: number, price: string, txFees: string = TRANSACTION_FEES){
    let val = ethers.parseEther(price) + ethers.parseEther(txFees);
    let tx = await contract.buyPacket(packetId, {value: val});
    await tx.wait();
    return tx;
}
  
async function getOwnerOfPacket(contract: Contract, packetId: number){
    return await contract.ownerOfPacket(packetId);
}
  
async function openPacket(contract: Contract, packetId: number, fees: string = PACKET_OPENING_FEES){
    let tx = await contract.openPacket(packetId, { value: ethers.parseEther(fees) });
    await tx.wait();
    return tx;
}
  
async function listPrompt(contract: Contract, promptId: number, price: string){
    let tx = await contract.listPrompt(promptId, ethers.parseEther(price));
    await tx.wait();
    return tx;
}
  
async function buyPrompt(contract: Contract, promptId: number, price: string, txFees: string = TRANSACTION_FEES){
    let val = ethers.parseEther(price) + ethers.parseEther(txFees);
    let tx = await contract.buyPrompt(promptId, {value: val});
    await tx.wait();
    return tx;
}
  
async function getOwnerOfPrompt(contract: Contract, promptId: number){
    return await contract.ownerOfPrompt(promptId);
}
  
async function createImage(contract: Contract, promptIds: number[], fees: string = GENERATION_FEES){
    let tx = await contract.createImage(promptIds, { value: ethers.parseEther(fees) });
    await tx.wait();
    return tx;
}
  
async function listImage(contract: Contract, imageId: number, price: string){
    let tx = await contract.listCard(imageId, ethers.parseEther(price));
    await tx.wait();
    return tx;
}
  
async function buyImage(contract: Contract, imageId: number, price: string, txFees: string = TRANSACTION_FEES){
    let val = ethers.parseEther(price) + ethers.parseEther(txFees);
    let tx = await contract.buyCard(imageId, {value: val});
    await tx.wait();
    return tx;
}
  
async function getOwnerOfImage(contract: Contract, imageId: number){
    return await contract.ownerOfCard(imageId);
}
  
async function destroyImage(contract: Contract, imageId: number, fees: string = DESTRUCTION_FEES){
    let tx = await contract.burnImageAndRecoverPrompts(imageId, {value: ethers.parseEther(fees)});
    await tx.wait();
    return tx;
}