import { ethers } from "hardhat";
import { TransactionReceipt } from "@ethersproject/abstract-provider";

// import * as fs from 'fs';

const contract_address = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

const owner_priv_key: string = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'


async function createCollection(contractName: string, collection: number = 1) {

    const wallet_owner = await ethers.getSigner(owner_priv_key);

    const contract_owner = await ethers.getContractAt(contractName, contract_address, wallet_owner)
    let tx = await contract_owner.forgeCollection(collection)
    await tx.wait();
    console.log("forgeCollection completed.");
    return;
}


async function main() {
    let collection = process.env.collection;
    if (collection == undefined) {
        console.log("collection is undefined");
        return;
    }
    let collection_int = parseInt(collection);
    if (isNaN(collection_int)) {
        console.log("collection is not a number");
        return;
    }

    const contract = await createCollection("MetaFusionPresident", collection_int);

}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
