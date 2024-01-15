import { ethers } from "hardhat";
// import * as fs from 'fs';

const contract_address = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

const owner_priv_key: string = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'

const other_priv_key: string = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
const other2_priv_key: string = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'

const collections = [1, 2]

var packets: { [id: string] : { [collection: string] : number[]} } = {};
packets[owner_priv_key] = {};
packets[other_priv_key] = {};

const FORGE_TOT_PACKETS = 3;


function genPKUUID(collection: number | bigint | boolean, idInCollection: number | bigint | boolean){
    return (BigInt(idInCollection) << BigInt(16)) | BigInt(collection)
}

async function connect(contractName: string) {

    const SIMULATE_PACKET_FORGE = true;
    const SIMULATE_PACKET_TRANSFER = true;
    const SIMULATE_PACKET_OPENING = true;
    
    const wallet_owner = await ethers.getSigner(owner_priv_key);
    
    const wallet_other = await ethers.getSigner(other_priv_key);

    const wallet_other2 = await ethers.getSigner(other2_priv_key);
    console.log('wallet_other: ', wallet_other.address);

    // connect to contract as owner and forge collection

    let args = { value: ethers.parseEther("0.1") }

    const contract_owner = await ethers.getContractAt(contractName, contract_address, wallet_owner)
    const contract_other = await ethers.getContractAt(contractName, contract_address, wallet_other2)

    const contracts = [contract_owner, contract_other]

    if (SIMULATE_PACKET_FORGE) {
        for (let i = 0; i < collections.length; i++) {
            let collection = collections[i]
            let tx = await contract_owner.forgeCollection(collection)
            await tx.wait();

            for (let x = 0; x < contracts.length; x++) {
                let cur_contract = contracts[x];
                let cur_address: string = await cur_contract.getAddress();
                packets[cur_address][collection] = [];
            }

            let tot_packets = 0;
            for (let j = 0; j < contracts.length; j++) {
                let cur_contract = contracts[j];
                let cur_address: string = await cur_contract.getAddress();

                for (let k = 0; k < FORGE_TOT_PACKETS; k++) {
                    let tx = await cur_contract.forgePacket(collection, args)
                    await tx.wait();
                    
                    tot_packets++;
                    packets[cur_address][collection].push(tot_packets);
                }
            }
        }
    }

    if (SIMULATE_PACKET_TRANSFER) {
        var collection = 1
        var packet_id = 1
        // seller lists packet for sale

        


        // buyer calls the willToBuy


        
        // get user2

    }


    if (SIMULATE_PACKET_OPENING) {
        let packet_id_start;

        for (let i = 0; i < collections.length; i++) {
            let collection = collections[i]
            let packet_id_end = collection & 0xffff
            
            let cur_contract = contract_owner;
            let next_contract = contract_other;

            for (let j = 0; j < packets.length; j++) {
                let packet_num = packets[j]
                packet_id_start = packet_num << 16;
                let packet_id = packet_id_start | packet_id_end;
                let tx = await cur_contract.openPacket(packet_id, args);
                await tx.wait();
                
                let tmp = cur_contract;
                cur_contract = next_contract;
                next_contract = tmp;
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