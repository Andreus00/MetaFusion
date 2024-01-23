// SPDX-License-Identifier: MIT

/**
 * This contract implements the packets for the MetaFusion system.
 * This is based on the ERC721 standard, but with some modifications.
 * 
 * Functions can only be called by the owner of the contract. In metafusion the owner is the MetaFusionPresident.
 */

pragma solidity ^0.8.19;

import "./Sellable.sol";

/**
 * ID: 0-15 collection
 *    16-31 packet id in collection
 * 	  [31, 30, 29, 28, 27, 26, 25, 24, 23, 22, ... , 3, 2, 1, 0]
 * 
 * @title 
 * @author 
 * @notice 
 */

contract MetaPacket is Sellable {

	/////////////// CONSTANTS ///////////////

	/**
	 * The maximum number of packets that can be minted for each collection.
	 */
	uint16 constant MAX_PACKETS_PER_COLLECTION = 750;  // The maximum number of packets that can be minted for each collection.

	// /**
	//  * The owner of the contract.
	//  */
	// address immutable private owner;

	/////////////// VARIABLES ///////////////

	/**
	 * Mapping from collection to the number of packets already minted for that collection. 0 if the collection does not exist.
	 * 
	 * Collections existance is handled by this packet.
	 * If a collection exists, users can mint packets for that collection.
	 */
	mapping (uint16 => uint16) public alreadyMinted;

	/////////////// MODIFIERS ///////////////

	/**
	 * Modifier to check if a collection exists.
	 */
    modifier collectionExists(uint16 _collection) {
        require(checkCollectionExistence(_collection), "The collection does not exist!");
        _;
    }
    
	/**
	 * Modifier to check if a collection does not exist.
	 */
	modifier collectionNotExists(uint16 _collection) {
        require(!checkCollectionExistence(_collection), "The collection exists!");
        _;
    }

	/**
	 * Modifier to check if a collection is full.
	 */
    modifier collectionIsNotFull(uint16 _collection) {
        require(_checkIfCollectionIsFull(_collection), "The collection is full!");
        _;
    }

	/**
	 * Modifier to check if the sender is the owner of the packet.
	 */
	modifier onlyPacketOwner(uint32 id, address opener) {
		require(opener == ownerOf(uint256(id)), "Only the owner of the packet can burn it!");
		_;
	}


	/////////////// CONSTRUCTOR ///////////////

	/**
	 * Constructor.
	 */
	constructor() Sellable("MetaPacket", "PKT") { // The name and symbol of the token
		// owner = msg.sender;    // The owner of the contract is the one who deployed it
	}


	/////////////// FUNCTIONS ///////////////
	
	/**
	 * Check if a collection exists.
	 */
	function checkCollectionExistence(uint16 _collection) public view returns (bool) {
		return alreadyMinted[_collection] > 0;
	}

	/**
	 * Check if a collection is full.
	 */
	function _checkIfCollectionIsFull(uint16 _collection) private view returns (bool) {
		return MAX_PACKETS_PER_COLLECTION > alreadyMinted[_collection];
	}

	/**
	 * Generate the UUID of a packet.
	 */
	function _genPKUUID(uint16 _collection, uint16 idInCollection) private pure returns (uint32) {
		return (uint32(idInCollection) << 16) | uint32(_collection);
	}

	/**
	 * Mint a packet.
	 * 
	 * Minting consists of generating new UUIDs for packets and storing them in 32 bits each.
	 * We then mint the packet with _safeMint (ERC721).
	 */
	function mint(address buyer, uint16 _collection) public collectionExists(_collection) collectionIsNotFull(_collection) onlyOwner returns(uint32){
		// calculate the kacchak of alreadyMinted[_collection] + _collection
		uint16 id = alreadyMinted[_collection];
		uint32 packetUUid32 = _genPKUUID(_collection, id);
		uint256 packetUUid = uint256(packetUUid32);

		_safeMint(buyer, packetUUid);
		alreadyMinted[_collection]++;

		return packetUUid32;
	}

	/**
	 * Forge a collection.
	 * 
	 * This function is called by the MetaFusionPresident when a collection is created.
	 * It sets the number of packets already minted for that collection to 1.
	 */
	function forgeCollection(uint16 _collection) public collectionNotExists(_collection) onlyOwner {
		alreadyMinted[_collection] = 1;
	}

	/**
	 * Opening a packet means burning the packet and generating new prompts.
	 * 
	 * This function is called by the MetaFusionPresident when a packet is opened.
	 * 
	 * Prompts are not generated here, but in the MetaFusionPresident.
	 */
	function openPacket(uint32 id) public onlyOwner onlyPacketOwner(id, tx.origin) {
		super.burn(uint256(id));
	}
}
