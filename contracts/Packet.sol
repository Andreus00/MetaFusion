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
    address private oracle;  // the oracle

    mapping (uint => uint) public collection;  // The collection to which the packet belongs. Everyone can read this.

    string public baseURI = "https://metafusion.io/api/packet/";  // The base URI for the metadata of the packets

    constructor() ERC721("MetaPacket", "PKT") { // The name and symbol of the token
        owner = msg.sender;    // The owner of the contract is the one who deployed it
    }

    function setOracle(address _oracle) public {
        // The owner of the contract is the only one who can set the oracle.
        require(msg.sender == owner, "Only the owner of the contract can set the oracle!");
        oracle = _oracle;
    }

    function mint(uint id, uint _collection) public {
        // The owner of the contract is the only one who can mint new packets.
        require(msg.sender == owner, "Only the owner of the contract can mint new MetaPackets!");
        _safeMint(owner, id);
        collection[id] = _collection;
    }

    function burn(uint id) public {
        require(msg.sender == ownerOf(id), "Only the owner of the packet can burn it!");
        
        // TODO: Call the oracle to mint the Prompts
        
        // Burn the packet
        _burn(id);
        // remove the packet from collection
        delete collection[id];
    }
}