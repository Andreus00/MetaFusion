// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./Prompt.sol";
import "./Packet.sol";
import "./Card.sol";


contract MetaFusionPresident {

    address private oracle;  // the oracle
    address immutable private owner;  // the owner of the contract

    MetaPrompt private metaPrompt;
    MetaPacket private metaPacket;
    MetaCard   private metaCard;

    uint constant packetCost = 0.1 ether;

    mapping (address => ImageMetadata[]) public metadata;  // The seed used to generate the image. Everyone can read this.

    string public baseURI = "https://metafusion.io/api/";  // The base URI for the metadata of the cards

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner of the contract can forge new collections!");
        _;
    }

    modifier checkPacketCost() {
        require(msg.value >= packetCost, "You didn't send enought ethers!");
        _;
    }

    constructor() { // The name and symbol of the token
        oracle = msg.sender;    // I still don't know how to use the oracle
        owner = msg.sender;    // The owner of the contract is the one who deployed it

        // create the meta contracts
        metaPacket = new MetaPacket();
        metaPrompt = new MetaPrompt();
        metaCard = new MetaCard();
    }

    /**
     * Forge a collection.
     * @param _collection The collection to forge
     */
    function forgeCollection(uint16 _collection) public onlyOwner {
        metaPacket.forgeCollection(_collection);
    }

    function checkCollectionExistence(uint16 collection) public view returns (bool) {
        return metaPacket.checkCollectionExistence(collection);        
    }

    function forgePacket(uint16 collection) public payable checkPacketCost {
        // metaPacket.
        metaPacket.mint(msg.sender, collection);
    }
}