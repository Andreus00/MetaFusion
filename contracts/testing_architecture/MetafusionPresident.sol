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

    string public baseURI = "https://metafusion.io/api/";  // The base URI for the metadata of the cards

    uint8 public constant NUM_PROMPT_TYPES = 6;  // The number of different prompt types
    uint8 public constant PACKET_SIZE = 8;  // The number of different prompt types
    uint256 private constant GENERATION_COST = 0.1 ether;  // The cost of generating an image

    event PacketForged(address indexed blacksmith, uint32 packetUUid);
    event PacketOpened(address indexed opener, uint32[] prompts);
    event CreateImage(address indexed creator, uint256 prompts);
    
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
        metaPacket = new MetaPacket(PACKET_SIZE);
        metaPrompt = new MetaPrompt(NUM_PROMPT_TYPES);
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

    function getPromptId(uint32 packetID, uint8 promptIndex, uint8 promptType) public pure returns (uint32) {
        uint32 shiftedPromptIndex = uint32(promptIndex) << (16 + 13);
        uint32 shiftedPromptType = uint32(promptType) << 13;
        return shiftedPromptIndex | shiftedPromptType | packetID;  // safe until we use less than 8192 packets per collection and less then 8192 collections
    }

    function openPacket(uint32 packetID) public payable {
        // metaPacket.
        metaPacket.openPacket(msg.sender, packetID);
        // todo: call the oracle and get the prompts
        // mock
        uint32[] memory prompts = new uint32[](PACKET_SIZE);
        for (uint8 i = 0; i < PACKET_SIZE; i++) {
            
            uint256 idhash = uint256(keccak256(abi.encodePacked(packetID, i, block.timestamp)));
            uint8 prompt_type = uint8(idhash % NUM_PROMPT_TYPES);

            uint32 promptId = getPromptId(packetID, i, prompt_type); // embedding informations

            // get the prompt type from the hash

            metaPrompt.mint(msg.sender, promptId);
            prompts[i] = promptId;
        }

        emit PacketOpened(msg.sender, prompts);
    }

    function getPromptsOwnebBy(address _address) public view returns (uint32[] memory) {
        return metaPrompt.getPromptsOwnebBy(_address);
    }

    function getCardsOwnedBy(address _address) public view returns (uint256[] memory) {
        return metaCard.getCardsOwnedBy(_address);
    }

    function mergePrompts(uint32[NUM_PROMPT_TYPES] memory prompts) private pure returns (uint256) {
        uint256 merged = 0;
        for (uint8 i = 0; i < NUM_PROMPT_TYPES; i++)
            merged = (merged << 32) | uint256(prompts[i]);
        return merged;
    }

    function createImage(uint32[NUM_PROMPT_TYPES] memory prompts) public payable {
        require(prompts.length == NUM_PROMPT_TYPES, string(abi.encodePacked("You shall pass the exact number of prompts: ", NUM_PROMPT_TYPES)));
        require(msg.value >= GENERATION_COST, "Not enough ether sent!");
        uint32[] memory prompts_array = new uint32[](NUM_PROMPT_TYPES);
        for (uint32 i = 0; i < NUM_PROMPT_TYPES; i++) {
            uint32 prompt_id = prompts[i];
            prompts_array[i] = prompt_id;
        }
        metaPrompt.burnForImageGeneration(msg.sender, prompts_array);

        // mint the card
        uint256 mergedPrompts = mergePrompts(prompts);
        uint256 cardId = metaCard.mint(msg.sender, mergedPrompts);

        emit CreateImage(msg.sender, cardId);
    }

    function burnImageAndRecoverPrompts(uint256 imageId) public payable {
        for(uint8 i = 0; i < NUM_PROMPT_TYPES; i++){
            imageId >>= 32;
            uint32 currentPromptId = uint32(imageId & 0xffffffff);
            metaPrompt.mint(msg.sender, currentPromptId);
        }
        
        metaCard.destroyCard(imageId);
    }
}