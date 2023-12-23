// SPDX-License-Identifier: MIT

/**
 * This contract implements the packets for the MetaFusion system.
 * This is based on the ERC721 standard, but with some modifications.
 * 
 * A packet can only be minted by the owner of the contract.
 * The owner of the contract is the only one who can terminate the contract.
 * The owner of a packet can decide to open it by burning it and getting 
 * some Prompts in return.
 * 
 * The unpack function burns the packet and calls the oracle to mint the Prompts.
 * 
 * The packet has a "collection" which is the collection to which the packet
 * belongs. This is stored in a mapping indexed by the packet id.
 * 
 * The packet can be transferred to another address.
 */

pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract MetaPacket is ERC721 {

	address private owner;  // the owner of the contract

	mapping (uint16 => uint16) public alreadyMinted;  // Mapping from collection to the number of packets already minted for that collection. 0 if the collection does not exist.

	uint16 constant MAX_PACKETS_PER_COLLECTION = 1000;  // The maximum number of packets that can be minted for each collection.

	string public baseURI = "https://metafusion.io/api/packet/";  // The base URI for the metadata of the packets; alias besughi
	
    modifier collectionExists(uint16 _collection) {
        require(checkCollectionExistence(_collection), "The collection does not exist!");
        _;
    }
    
	modifier collectionNotExists(uint16 _collection) {
        require(!checkCollectionExistence(_collection), "The collection exists!");
        _;
    }

    modifier collectionIsNotFull(uint16 _collection) {
        require(checkIfCollectionIsFull(_collection), "The collection is full!");
        _;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner of the contract can mint new MetaPackets!");
        _;
    }

	modifier onlyOwnerMintsCollections() {
        require(msg.sender == owner, "Only the owner of the contract can forge new collections!");
        _;
    }

	constructor() ERC721("MetaPacket", "PKT") { // The name and symbol of the token
		owner = msg.sender;    // The owner of the contract is the one who deployed it
	}

	function checkCollectionExistence(uint16 _collection) public view returns (bool) {
		return alreadyMinted[_collection] > 0;
	}
	function checkIfCollectionIsFull(uint16 _collection) public view returns (bool) {
		return MAX_PACKETS_PER_COLLECTION > alreadyMinted[_collection];
	}

	function genPKUUID(uint16 _collection, uint16 idInCollection) public pure returns (uint32) {
		return uint32(idInCollection) << 16 | uint32(_collection);
	}
	function getPacketIdInCollectionFromPKUUID(uint32 pkUuid) public pure returns (uint16) {
		return uint16(pkUuid >> 16); //& 0xffff; //Commented because we don't have any more field encoded
	}
	function getCollectionIdFromPKUUID(uint32 pkUuid) public pure returns (uint16) {
		return uint16(pkUuid & 0xffff);
	}

	function mint(address buyer, uint16 _collection) public collectionExists(_collection) collectionIsNotFull(_collection) onlyOwner{
		// calculate the kacchak of alreadyMinted[_collection] + _collection
		uint16 id = alreadyMinted[_collection];
		uint256 packetUUid = uint256(genPKUUID(_collection, id));
		_safeMint(buyer, packetUUid);
		alreadyMinted[_collection]++;
	}

	function forgeCollection(uint16 _collection) public collectionNotExists(_collection) onlyOwnerMintsCollections {
		alreadyMinted[_collection] = 1;
	}

	function openPacket(uint16 id) public payable {
		// TODO: check if the owner sent enough ether to open the packet
		require(msg.sender == ownerOf(id), "Only the owner of the packet can burn it!");

		// get the current timestamp
		uint256 timestamp = block.timestamp;

		uint256 seed = uint256(keccak256(abi.encodePacked(id, timestamp)));		
		
		// TODO: Call the oracle to mint the Prompts
		// TODO: mock the oracle for now



		// Burn the packet
		_burn(uint256(id));
	}
}
