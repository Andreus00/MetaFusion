// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./Prompt.sol";
import "./Packet.sol";
import "./Card.sol";


contract MetaFusionPresident {


    /////////////// VARIABLES ///////////////

    address immutable private owner;  // the owner of the contract

    MetaPrompt private metaPrompt;
    MetaPacket private metaPacket;
    MetaCard   private metaCard;

    uint256 constant PACKET_COST = 0.1 ether;
    uint256 constant PACKET_OPENING_FEES = 0.01 ether;
    uint256 constant GENERATION_FEES = 0.1 ether;  // The cost of generating an image
    uint256 constant DESTRUCTION_FEES = 0.001 ether;  // The fees for image destruction
    uint256 constant TRANSACTION_FEES = 0.01 ether;  // The fees for the transaction

    uint8 public constant NUM_PROMPT_TYPES = 6;  // The number of different prompt types
    uint8 public constant PACKET_SIZE = 8;  // The number of different prompt types

    /////////////// EVENTS ///////////////

    event PacketForged(address indexed blacksmith, uint32 packetId);
    event PacketOpened(address indexed opener, uint32[] prompts);

    event PromptCreated(uint256 IPFSCid, uint32 promptId, address to);
    
    event CreateImage(address indexed creator, uint256 cardId);
    event ImageCreated(uint256 IPFSCid, uint256 imageId, address indexed creator);
    event DestroyImage(uint256 imageId, address indexed userId);
    
    event WillToBuyPacket(address buyer, address seller, uint256 id, uint256 value);
    event WillToBuyPrompt(address buyer, address seller, uint256 id, uint256 value);
    event WillToBuyImage(address buyer, address seller, uint256 id, uint256 value);
    
    event PromptTransfered(address indexed buyer, address indexed seller, uint256 id, uint256 value);
    event PacketTransfered(address indexed buyer, address indexed seller, uint256 id, uint256 value);
    event CardTransfered(address indexed buyer, address indexed seller, uint256 id, uint256 value);
    
    event UpdateListPrompt(uint32 id, uint256 price, bool isListed);
    event UpdateListPacket(uint32 id, uint256 price, bool isListed);
    event UpdateListImage(uint256 id, uint256 price, bool isListed);

    /////////////// MODIFIERS ///////////////

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner of the contract can perform this action!");
        _;
    }

    modifier checkCost(uint256 cost) {
        require(msg.value >= cost, "You didn't send enought ethers!");
        _;
    }

    modifier isPacketListed(uint32 packetId) {
        require(metaPacket.getApproved(packetId) == address(this), "The packet is not listed!");
        _;
    }

    modifier isPromptListed(uint32 promptId) {
        require(metaPrompt.getApproved(promptId) == address(this), "The prompt is not listed!");
        _;
    }

    modifier isCardListed(uint256 cardId) {
        require(metaCard.getApproved(cardId) == address(this), "The card is not listed!");
        _;
    }

    modifier isOwnerOf(uint256 tokenId, ERC721 meta) {
        require(meta.ownerOf(tokenId) == msg.sender, "You are not the owner of the token!");
        _;
    }

    /////////////// CONSTRUCTOR ///////////////

    constructor() { // The name and symbol of the token
        owner = msg.sender;    // The owner of the contract is the one who deployed it

        // create the meta contracts
        metaPacket = new MetaPacket();
        metaPrompt = new MetaPrompt(NUM_PROMPT_TYPES);
        metaCard = new MetaCard();
    }

    /////////////// FUNCTIONS ///////////////

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

    function forgePacket(uint16 collection) public payable checkCost(PACKET_COST) {
        // Forge a metaPacket.
        uint32 packetUUid = metaPacket.mint(msg.sender, collection);
        emit PacketForged(msg.sender, packetUUid);
    }

    function _getPromptId(uint32 packetID, uint8 promptIndex, uint8 promptType) private pure returns (uint32) {
        uint32 shiftedPromptIndex = uint32(promptIndex) << (16 + 13);
        uint32 shiftedPromptType = uint32(promptType) << 13;
        return shiftedPromptIndex | shiftedPromptType | packetID;  // safe until we use less than 8192 packets per collection and less then 8192 collections
    }

    function openPacket(uint32 packetID) public payable checkCost(PACKET_OPENING_FEES){
        // metaPacket.
        metaPacket.openPacket(packetID);

        uint32[] memory prompts = new uint32[](PACKET_SIZE);
        for (uint8 i = 0; i < PACKET_SIZE; i++) {
            
            uint256 idhash = uint256(keccak256(abi.encodePacked(packetID, i, block.timestamp)));
            uint8 prompt_type = uint8(idhash % NUM_PROMPT_TYPES);

            uint32 promptId = _getPromptId(packetID, i, prompt_type); // embedding informations

            metaPrompt.mint(msg.sender, promptId);
            prompts[i] = promptId;
        }

        emit PacketOpened(msg.sender, prompts);
    }

    function promptMinted(uint256 IPFSCid, uint32 promptId, address to) public onlyOwner {
        emit PromptCreated(IPFSCid, promptId, to);
    }

    function _mergePrompts(uint32[NUM_PROMPT_TYPES] memory prompts) private pure returns (uint256) {
        uint256 merged = 0;
        for (uint8 i = 0; i < NUM_PROMPT_TYPES; i++)
            merged = (merged << 32) | uint256(prompts[i]);
        return merged;
    }

    function createImage(uint32[NUM_PROMPT_TYPES] memory prompts) public payable checkCost(GENERATION_FEES) {
        require(prompts.length == NUM_PROMPT_TYPES, string(abi.encodePacked("You shall pass the exact number of prompts: ", NUM_PROMPT_TYPES)));
        uint32[] memory prompts_array = new uint32[](NUM_PROMPT_TYPES);
        for (uint32 i = 0; i < NUM_PROMPT_TYPES; i++) {
            uint32 prompt_id = prompts[i];
            prompts_array[i] = prompt_id;
        }
        metaPrompt.burnForImageGeneration(msg.sender, prompts_array);

        // mint the card
        uint256 mergedPrompts = _mergePrompts(prompts);
        uint256 cardId = metaCard.mint(msg.sender, mergedPrompts);
        // emit event
        emit CreateImage(msg.sender, cardId);
    }

    function imageMinted(uint256 IPFSCid, uint256 imageId, address to) public onlyOwner {
        emit ImageCreated(IPFSCid, imageId, to);
    }

    function burnImageAndRecoverPrompts(uint256 imageId) public payable checkCost(DESTRUCTION_FEES) isOwnerOf(imageId, metaCard){
        metaCard.destroyCard(imageId);
        uint256 imageIdShifted = imageId >> 64; //remove seed
        for(uint8 i = 0; i < NUM_PROMPT_TYPES; i++){
            uint32 currentPromptId = uint32(imageIdShifted & 0xffffffff);
            if (currentPromptId != 0){
                // avoid minting non existing prompts IDs
                metaPrompt.mint(msg.sender, currentPromptId);
            }
            imageIdShifted = imageIdShifted >> 32;
        }

        emit DestroyImage(imageId, msg.sender);
    }

    /**
     * This function can be called by users to express their will to buy a packet.
     * They have to send an amount of ethers. An oracle will check if the amount is enough
     * and, if so, it will call the 'transferPacket' function.
     * @param packetId the id of the packet to buy
     */
    function buyPacket(uint32 packetId) public payable isPacketListed(packetId) {
        // this function registers the will of the buyer to buy a listed packet
        address seller = metaPacket.ownerOf(packetId);
        emit WillToBuyPacket(msg.sender, seller, packetId, msg.value - TRANSACTION_FEES);
    }

    /**
     * This function can be called by users to express their will to buy a prompt.
     * They have to send an amount of ethers. An oracle will check if the amount is enough
     * and, if so, it will call the 'transferPrompt' function.
     * @param promptId the id of the prompt to buy
     */
    function buyPrompt(uint32 promptId) public payable isPromptListed(promptId) {
        // this function registers the will of the buyer to buy a listed prompt
        address seller = metaPrompt.ownerOf(promptId);
        emit WillToBuyPrompt(msg.sender, seller, promptId, msg.value - TRANSACTION_FEES);
    }

    /**
     * This function can be called by users to express their will to buy a card.
     * They have to send an amount of ethers. An oracle will check if the amount is enough
     * and, if so, it will call the 'transferCard' function.
     * @param cardId the id of the card to buy
     */
    function buyCard(uint256 cardId) public payable isCardListed(cardId) {
        // this function registers the will of the buyer to buy a listed card
        address seller = metaCard.ownerOf(cardId);
        emit WillToBuyImage(msg.sender, seller, cardId, msg.value - TRANSACTION_FEES);
    }

    /**
     * This function allows the contract to send ether to an address.
     * This is used to send ethers to the seller when a packet is sold.
     * @param _to the address to send the ether to
     * @param value the amount of ether to send
     */
    function _payAddress(address _to, uint256 value) private {
        (bool sent, bytes memory data) = _to.call{value: value}("");
        require(sent, "Failed to send Ether");
    }


    /**
     * This function allows the owner to transfer a packet to a buyer and 
     * @param buyer the buyer
     * @param seller the seller
     * @param packetId the image to transfer
     * @param val the amount of ether to send to the seller
     */
    function transferPacket(address buyer, address seller, uint32 packetId, uint256 val) public isPacketListed(packetId) onlyOwner {
        _payAddress(seller, val);
        metaPacket.transferFrom(seller, buyer, packetId);
        emit PacketTransfered(buyer, seller, packetId, val);
    }

    /**
     * This function allows the owner to transfer a prompt to a buyer and send ethers to the seller.
     * @param buyer the buyer
     * @param seller the seller
     * @param promptId the prompt to transfer
     * @param val the amount of ether to send to the seller
     */
    function transferPrompt(address buyer, address seller, uint32 promptId, uint256 val) public isPromptListed(promptId) onlyOwner {
        _payAddress(seller, val);
        metaPrompt.transferFrom(seller, buyer, promptId);
        emit PromptTransfered(buyer, seller, promptId, val);
    }

    /**
     * This function allows the owner to transfer a card to a buyer and send ethers to the seller.
     * @param buyer the buyer
     * @param seller the seller
     * @param imageId the image to transfer
     * @param val the amount of ether to send to the seller
     */
    function transferCard(address buyer, address seller, uint256 imageId, uint256 val) public isCardListed(imageId) onlyOwner {
        _payAddress(seller, val);
        metaCard.transferFrom(seller, buyer, imageId);
        emit CardTransfered(buyer, seller, imageId, val);
    }


    /**
     * If the buyer doesn't send enough ether, the owner can refund him.
     * @param buyer the address that will receive the refund
     * @param value the amount of ether to send
     */
    function refund(address buyer, uint256 value) public onlyOwner {
        _payAddress(buyer, value);
    }

    function getPacketURI(uint32 packetId) public view returns (string memory) {
        return metaPacket.tokenURI(packetId);
    }

    function getPromptURI(uint32 promptId) public view returns (string memory) {
        return metaPrompt.tokenURI(promptId);
    }

    function getCardURI(uint256 cardId) public view returns (string memory) {
        return metaCard.tokenURI(cardId);
    }

    function listPrompt(uint32 promptId, uint256 price) public {
        metaPrompt.approve(address(this), promptId);
        emit UpdateListPrompt(promptId, price, true);
    }

    function listPacket(uint32 packetId, uint256 price) public {
        metaPacket.approve(address(this), packetId);
        emit UpdateListPacket(packetId, price, true);
    }

    function listCard(uint256 cardId, uint256 price) public {
        metaCard.approve(address(this), cardId);
        emit UpdateListImage(cardId, price, true);
    }

    function unlistPrompt(uint32 promptId) public {
        metaPrompt.approve(address(0), promptId);
        emit UpdateListPrompt(promptId, 0, false);
    }

    function unlistPacket(uint32 packetId) public {
        metaPacket.approve(address(0), packetId);
        emit UpdateListPacket(packetId, 0,  false);
    }

    function unlistCard(uint256 cardId) public {
        metaCard.approve(address(0), cardId);
        emit UpdateListImage(cardId, 0, false);
    }
}