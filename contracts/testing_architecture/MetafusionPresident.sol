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

    event PacketForged(address indexed blacksmith, uint32 packetUUid);

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

    function ownerOfPacket(uint256 _tokenId) public view returns (address) {
        return metaPacket.ownerOf(_tokenId);
    }
    
    function ownerOfPrompt(uint256 _tokenId) public view returns (address) {
        return metaPrompt.ownerOf(_tokenId);
    }

    function ownerOfCard(uint256 _tokenId) public view returns (address) {
        return metaCard.ownerOf(_tokenId);
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

    function forgePacket(uint16 collection) public payable checkPacketCost{
        // metaPacket.
        uint32 packetUUid = metaPacket.mint(msg.sender, collection);
        emit PacketForged(msg.sender, packetUUid);
    }

    function openPacket(uint32 packetID) public {
        // metaPacket.
        uint256 generation_seed;
        uint16 collection;
        (generation_seed, collection) = metaPacket.openPacket(msg.sender, packetID);
        // todo: call the oracle and get the prompts
        // mock
        for (uint8 i = 0; i < 6; i++) {
            uint256 card_id = uint256(keccak256(abi.encodePacked(generation_seed, i)));
            metaPrompt.mint(msg.sender, card_id, collection, i);
        }
    }

    function getPromptList(address _address) public view returns (uint[] memory) {
        return metaPrompt.getPromptList(_address);
    }
}