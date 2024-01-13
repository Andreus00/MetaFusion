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

/**
 * ID: 0-15 collection
 *    16-31 packet id in collection
 * 	  [31, 30, 29, 28, 27, 26, 25, 24, 23, 22, ... , 3, 2, 1, 0]
 * 
 * @title 
 * @author 
 * @notice 
 */

contract MetaPacket is ERC721 {

	address private owner;  // the owner of the contract

	mapping (uint16 => uint16) public alreadyMinted;  // Mapping from collection to the number of packets already minted for that collection. 0 if the collection does not exist.

	uint16 constant MAX_PACKETS_PER_COLLECTION = 1000;  // The maximum number of packets that can be minted for each collection.
	uint8 immutable private PACKET_SIZE;

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
	
	modifier onlyPacketOwner(uint32 id, address opener) {
		require(opener == ownerOf(uint256(id)), "Only the owner of the packet can burn it!");
		_;
	}

	modifier exitsPacket(uint32 id) {
		_requireOwned(uint256(id));
		_;
	}

	constructor(uint8 _PACKET_SIZE) ERC721("MetaPacket", "PKT") { // The name and symbol of the token
		owner = msg.sender;    // The owner of the contract is the one who deployed it
		PACKET_SIZE = _PACKET_SIZE;
	}

	function checkCollectionExistence(uint16 _collection) public view returns (bool) {
		return alreadyMinted[_collection] > 0;
	}
	function checkIfCollectionIsFull(uint16 _collection) public view returns (bool) {
		return MAX_PACKETS_PER_COLLECTION > alreadyMinted[_collection];
	}
	function genPKUUID(uint16 _collection, uint16 idInCollection) public pure returns (uint32) {
		return (uint32(idInCollection) << 16) | uint32(_collection);
	}
	function getPacketIdInCollectionFromPKUUID(uint32 pkUuid) public pure returns (uint16) {
		return uint16(pkUuid >> 16); //& 0xffff; //Commented because we don't have any more field encoded
	}
	function getCollectionIdFromPKUUID(uint32 pkUuid) public pure returns (uint16) {
		return uint16(pkUuid & 0xffff);
	}

	function mint(address buyer, uint16 _collection) public collectionExists(_collection) collectionIsNotFull(_collection) onlyOwner returns(uint32){
		// calculate the kacchak of alreadyMinted[_collection] + _collection
		uint16 id = alreadyMinted[_collection];
		uint32 packetUUid32 = genPKUUID(_collection, id);
		uint256 packetUUid = uint256(packetUUid32);

		_safeMint(buyer, packetUUid);
		alreadyMinted[_collection]++;

		return packetUUid32;
	}

	function forgeCollection(uint16 _collection) public collectionNotExists(_collection) onlyOwnerMintsCollections {
		alreadyMinted[_collection] = 1;
	}

	function makePromptID() public returns (uint64) {

	}

	function openPacket(address opener, uint32 id) public payable onlyOwner onlyPacketOwner(id, opener) {
		_burn(uint256(id));
	}
}
