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

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract MetaPacket is ERC721 {

    address private owner;  // the owner of the contract

    mapping (uint => uint) public collection;  // The collection to which the packet belongs. Everyone can read this.
    mapping (uint => uint) public alreadyMinted;  // Mapping from collection to the number of packets already minted for that collection.
    mapping (uint => bool) public existCollection; // Mapping from collection to a boolean that indicates if the collection exists.

    uint constant MAX_PACKETS_PER_COLLECTION = 1000;  // The maximum number of packets that can be minted for each collection.

    string public baseURI = "https://metafusion.io/api/packet/";  // The base URI for the metadata of the packets; alias besughi

    constructor() ERC721("MetaPacket", "PKT") { // The name and symbol of the token
        owner = msg.sender;    // The owner of the contract is the one who deployed it
    }

    function mint(address buyer, uint _collection) public {
        // The owner of the contract is the only one who can mint new packets.
        require(msg.sender == owner, "Only the owner of the contract can mint new MetaPackets!");
        require(existCollection[_collection], "The collection does not exist!");
        require(MAX_PACKETS_PER_COLLECTION > alreadyMinted[_collection], "The maximum number of packets for this collection has been reached!");
        _safeMint(buyer, alreadyMinted[_collection]);
        collection[alreadyMinted[_collection]] = _collection;
        alreadyMinted[_collection]++;
    }

    function checkCollectionExistence(uint _collection) public view returns (bool) {
        return existCollection[_collection];
    }

    function forgeCollection(uint _collection) public {
        // The owner of the contract is the only one who can forge new collections.
        require(msg.sender == owner, "Only the owner of the contract can forge new collections!");
        require(!existCollection[_collection], "The collection already exists!");
        existCollection[_collection] = true;
    }

    function openPacket(uint id) public payable {
        // TODO: check if the owner sent enough ether to open the packet
        require(msg.sender == ownerOf(id), "Only the owner of the packet can burn it!");
        
        // TODO: Call the oracle to mint the Prompts
        // TODO: mock the oracle for now

        // Burn the packet
        _burn(id);
        // remove the packet from collection
        delete collection[id];
    }
}
