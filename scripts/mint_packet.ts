import { ethers } from "hardhat";
// import * as fs from 'fs';

const owner_priv_key = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'

const other_priv_key = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'

async function connect(contractName: string) {

    const SIMULATE_PACKET_FORGE = true;
    const SIMULATE_PACKET_OPENING = true;
    
    const wallet_owner = await ethers.getSigner(owner_priv_key);
    // console.log('wallet_owner: ', wallet_owner.address);
    const wallet_other = await ethers.getSigner(other_priv_key);
    console.log('wallet_other: ', wallet_other.address);

    // connect to contract as owner and forge collection

    let args = { value: ethers.parseEther("0.1") }

    if (SIMULATE_PACKET_FORGE) {
        for (let i = 1; i <= 2; i++) {
            var contract_owner= await ethers.getContractAt(contractName, "0x5fbdb2315678afecb367f032d93f642f64180aa3", wallet_owner)
            let tx = await contract_owner.forgeCollection(i)
            await tx.wait();
            for (let j = 1; j <= 2; j++) {
                let tx = await contract_owner.forgePacket(i, args)
                await tx.wait();
                
                // connect to contract as other and forge packet
                var contract_other = await ethers.getContractAt(contractName, "0x5fbdb2315678afecb367f032d93f642f64180aa3", wallet_other)
                let tx2 = await contract_other.forgePacket(i, args)
                await tx2.wait();
            }
        }
    }


    if (SIMULATE_PACKET_OPENING) {
        let packet_id_start;

        for (let i = 1; i <= 2; i++) {
            var contract_owner= await ethers.getContractAt(contractName, "0x5fbdb2315678afecb367f032d93f642f64180aa3", wallet_owner)
            let packet_id_end = i & 0xffff
            let packet_num = 0;
            for (let j = 1; j <= 2; j++) {
                packet_num ++;
                packet_id_start = packet_num << 16;
                let packet_id = packet_id_start | packet_id_end;
                let tx = await contract_owner.openPacket(packet_id, args);
                await tx.wait();
                
                packet_num ++;
                packet_id_start = packet_num << 16;
                packet_id = packet_id_start | packet_id_end;
                // connect to contract as other and forge packet
                var contract_other = await ethers.getContractAt(contractName, "0x5fbdb2315678afecb367f032d93f642f64180aa3", wallet_other);
                let tx2 = await contract_other.openPacket(packet_id, args);
                await tx2.wait();
            }
        }
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