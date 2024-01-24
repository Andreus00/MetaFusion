// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;


import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./Prompt.sol";
import "./Packet.sol";
import "./Card.sol";


/**
 * This contract is the main contract of the MetaFusion project.
 * Users can forge packets, open them, generate images and destroy them through this contract.
 * They can also buy and sell packets, prompts and images.
 * 
 * The contract is the owner of the MetaPacket, MetaPrompt and MetaCard contracts.
 * It is the only one who can mint new tokens.
 * 
 * The owner of this contract is also used as oracle to generate prompts, images and to transfer packets.
 * 
 * @title MetaFusionPresident
 * @author 
 * @notice 
 */
contract MetaFusionPresident {

    /////////////// CONSTANTS ///////////////
    /**
     * @dev The owner of the contract. The owner is the only address that can call
     */
    address immutable private owner;  // Owner of the contract

    /**
     * @notice The hash of the project. This is used to verify the authenticity of the project.
     */
    uint128 private project_hash;

    /**
     * @dev The cost of a packet. This is the amount of ether that a user has to send to forge a packet.
     */
    uint256 constant PACKET_COST = 0.1 ether;
    /**
     * @dev The cost of opening a packet. This is the amount of ether that a user has to send to open a packet.
     */
    uint256 constant PACKET_OPENING_FEES = 0.01 ether;
    /**
     * @dev The cost of generating an image. This is the amount of ether that a user has to send to generate an image.
     */
    uint256 constant GENERATION_FEES = 0.1 ether;  // Cost of generating an image
    /**
     * @dev The cost of destroying an image. This is the amount of ether that a user has to send to destroy an image.
     */
    uint256 constant DESTRUCTION_FEES = 0.001 ether;  // Fees for image destruction
    /**
     * @dev The cost of a transaction. This is the amount of ether that a user has to send to perform a transaction.
     */
    uint256 constant TRANSACTION_FEES = 0.001 ether;  // Fees for the transaction
    /**
     * @dev The number of different prompt types. (Character, hat, handoff, ...)
     */
    uint8 public constant NUM_PROMPT_TYPES = 6;  // Number of different prompt types
    /**
     * @dev The number of prompts in a packet.
     */
    uint8 public constant PACKET_SIZE = 8;  // Number of different prompt types

    /////////////// VARIABLES ///////////////

    /**
     * @dev The MetaPrompt contract. This contract is an ERC721. It is used to keep track of the prompts.
     */
    MetaPrompt private metaPrompt;
    /**
     * @dev The MetaPacket contract. This contract is an ERC721. It is used to keep track of the packets.
     */
    MetaPacket private metaPacket;
    /**
     * @dev The MetaCard contract. This contract is an ERC721. It is used to keep track of the images.
     */
    MetaCard   private metaCard;

    /////////////// EVENTS ///////////////

    /**
     * Event emitted when a packet is forged by an user.
     * @param blacksmith the address of the account that forged the packet
     * @param packetId the id of the packet
     */
    event PacketForged(address indexed blacksmith, uint32 packetId);
    /**
     * Event emitted when a packet is opened by an user.
     * @param opener the opener of the packet
     * @param prompts IDs of the prompts that were generated
     */
    event PacketOpened(address indexed opener, uint32[] prompts);

    /**
     * Event emitted when a prompt is created by the oracle.
     * @param IPFSCid IPFS CID associated to the metadata of the prompt
     * @param promptId id of the prompt
     * @param to address of the user that minted the prompt
     */
    event PromptCreated(uint256 IPFSCid, uint32 promptId, address to);
    
    /**
     * Event emitted when an user creates an image. 
     * This event is catched by the oracle who will generate the image and push it to IPFS.
     * @param creator the minter of the card.
     * @param cardId the id of the card.
     */
    event CreateImage(address indexed creator, uint256 cardId);
    /**
     * Event emitted when an image is created by the oracle.
     * @param IPFSCid IPFS CID associated to the image
     * @param imageId id of the image
     * @param creator minter of the image
     */
    event ImageCreated(uint256 IPFSCid, uint256 imageId, address indexed creator);
    /**
     * Event emitted when an image is destroyed by an user.
     * @param imageId id of the image
     * @param userId address of the user that destroyed the image
     */
    event DestroyImage(uint256 imageId, address indexed userId);

    
    /**
     * Event emitted when a packet is transfered from a seller to a buyer.
     * @param buyer the buyer
     * @param seller the seller
     * @param id the id of the packet
     * @param value the amount of ether sent to the seller
     */
    event PacketTransfered(address indexed buyer, address indexed seller, uint256 id, uint256 value);
    /**
     * Event emitted when a prompt is transfered from a seller to a buyer.
     * @param buyer the buyer
     * @param seller the seller
     * @param id the id of the prompt
     * @param value the amount of ether sent to the seller
     */
    event PromptTransfered(address indexed buyer, address indexed seller, uint256 id, uint256 value);
    /**
     * Event emitted when an image is transfered from a seller to a buyer.
     * @param buyer the buyer
     * @param seller the seller
     * @param id the id of the image
     * @param value the amount of ether sent to the seller
     */
    event CardTransfered(address indexed buyer, address indexed seller, uint256 id, uint256 value);
    
    /**
     * Event emitted when a packet is listed or unlisted.
     * @param id the id of the packet
     * @param price the price of the packet
     * @param isListed true if the packet is listed, false otherwise
     * @param tokenOwner address of the token owner
     */
    event UpdateListPrompt(uint32 id, uint256 price, bool isListed, address tokenOwner);
    /**
     * Event emitted when a prompt is listed or unlisted.
     * @param id the id of the prompt
     * @param price the price of the prompt
     * @param isListed true if the prompt is listed, false otherwise
     * @param tokenOwner address of the token owner
     */
    event UpdateListPacket(uint32 id, uint256 price, bool isListed, address tokenOwner);
    /**
     * Event emitted when an image is listed or unlisted.
     * @param id the id of the image
     * @param price the price of the image
     * @param isListed true if the image is listed, false otherwise
     * @param tokenOwner address of the token owner
     */
    event UpdateListImage(uint256 id, uint256 price, bool isListed, address tokenOwner);

    /////////////// MODIFIERS ///////////////

    /**
     * This modifier checks if the sender is the owner of the contract.
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner of the contract can perform this action!");
        _;
    }

    /**
     * This modifier checks if the sender sent enough ethers. Used for fees.
     * @param cost the amount of ethers that the sender has to send
     */
    modifier checkCost(uint256 cost) {
        require(msg.value >= cost, "You didn't send enought ethers!");
        _;
    }

    /**
     * This modifer checks if the token is listed.
     * @param tokenId the id of the token
     * @param meta the meta contract of the token
     */
    modifier isTokenListed(uint256 tokenId, Sellable meta) {
        require(meta.isTokenListed(tokenId), "The token is not listed!");
        _;
    }


    /**
     * This modifier checks if the sender is the owner of the token.
     * @param tokenId the id of the token
     * @param meta the meta contract of the token
     */
    modifier isOwnerOf(uint256 tokenId, ERC721 meta) {
        require(meta.ownerOf(tokenId) == msg.sender, "You are not the owner of the token!");
        _;
    }

    /////////////// CONSTRUCTOR ///////////////

    constructor() {
        // set the owner
        owner = msg.sender;

        // create the meta contracts
        metaPacket = new MetaPacket();
        metaPrompt = new MetaPrompt(NUM_PROMPT_TYPES);
        metaCard = new MetaCard();
    }

    /////////////// FUNCTIONS ///////////////

    function setProjectHash(uint128 _project_hash) public onlyOwner {
        project_hash = _project_hash;
    }

    function getProjectHash() public view returns (uint256) {
        return project_hash;
    }


    /**
     * Get the owner of a packet.
     * @param _tokenId the id of the packet
     */
    function ownerOfPacket(uint256 _tokenId) public view returns (address) {
        return metaPacket.ownerOf(_tokenId);
    }
    /**
     * Get the owner of a prompt.
     * @param _tokenId the id of the prompt
     */
    function ownerOfPrompt(uint256 _tokenId) public view returns (address) {
        return metaPrompt.ownerOf(_tokenId);
    }
    /**
     * Get the owner of a card.
     * @param _tokenId the id of the card
     */
    function ownerOfCard(uint256 _tokenId) public view returns (address) {
        return metaCard.ownerOf(_tokenId);
    }

    /**
     * Forge a collection. Only the owner of the contract can call this function.
     * @param _collection The collection to forge
     */
    function forgeCollection(uint16 _collection) public onlyOwner {
        metaPacket.forgeCollection(_collection);
    }

    /**
     * Check if a collection exists.
     * @param collection the collection to check
     */
    function checkCollectionExistence(uint16 collection) public view returns (bool) {
        return metaPacket.checkCollectionExistence(collection);        
    }

    /**
     * Forge a packet. The sender has to send enough ethers.
     * This function is called by the user when he wants to mint a packet.
     * @param collection the collection of the packet
     */
    function forgePacket(uint16 collection) public payable checkCost(PACKET_COST) {
        // Forge a metaPacket.
        uint32 packetUUid = metaPacket.mint(msg.sender, collection);
        emit PacketForged(msg.sender, packetUUid);
    }

    /**
     * Get the id of a prompt.
     * @param packetID the id of the packet
     * @param promptIndex the index of the prompt in the packet
     * @param promptType the type of the prompt
     */
    function _getPromptId(uint32 packetID, uint8 promptIndex, uint8 promptType) private pure returns (uint32) {
        uint32 shiftedPromptIndex = uint32(promptIndex) << (16 + 13);
        uint32 shiftedPromptType = uint32(promptType) << 13;
        return shiftedPromptIndex | shiftedPromptType | packetID;  // safe until we use less than 8192 packets per collection and less then 8192 collections
    }

    /**
     * Open a packet. The sender has to send enough ethers.
     * This function is called by the user when he wants to open a packet.
     * @param packetID the id of the packet to open
     */
    function openPacket(uint32 packetID) public payable checkCost(PACKET_OPENING_FEES){
        // destroy the packet.
        metaPacket.openPacket(packetID);

        // mint the prompts
        uint32[] memory prompts = new uint32[](PACKET_SIZE);
        for (uint8 i = 0; i < PACKET_SIZE; i++) {
            // pseudo random prompt type
            uint256 idhash = uint256(keccak256(abi.encodePacked(packetID, i, block.timestamp)));
            uint8 prompt_type = uint8(idhash % NUM_PROMPT_TYPES);

            // mint the prompt
            uint32 promptId = _getPromptId(packetID, i, prompt_type); // embedding informations
            metaPrompt.mint(msg.sender, promptId);
            prompts[i] = promptId;
        }
        
        // emit event
        emit PacketOpened(msg.sender, prompts);
    }

    /**
     * Function called by the oracle to publish the IPFS CID.
     * @param IPFSCid IPFS CID associated to the metadata of the prompt
     * @param promptId id of the prompt
     * @param to address of the user that minted the prompt
     */
    function promptMinted(uint256 IPFSCid, uint32 promptId, address to) public onlyOwner {
        emit PromptCreated(IPFSCid, promptId, to);
    }

    /**
     * Merge the prompts into a single uint256.
     * @param prompts the prompts to merge
     */
    function _mergePrompts(uint32[NUM_PROMPT_TYPES] memory prompts) private pure returns (uint256) {
        uint256 merged = 0;
        for (uint8 i = 0; i < NUM_PROMPT_TYPES; i++)
            merged = (merged << 32) | uint256(prompts[i]);
        return merged;
    }

    /**
     * Create an image. The sender has to send enough ethers.
     * This function is called by the user when he wants to generate an image.
     * @param prompts the prompts to use to generate the image
     */
    function createImage(uint32[NUM_PROMPT_TYPES] memory prompts) public payable checkCost(GENERATION_FEES) {
        // check if the user sent the exact number of prompts
        require(prompts.length == NUM_PROMPT_TYPES, string(abi.encodePacked("You shall pass the exact number of prompts: ", NUM_PROMPT_TYPES)));

        // burn the prompts.
        uint32[] memory prompts_array = new uint32[](NUM_PROMPT_TYPES);
        for (uint32 i = 0; i < NUM_PROMPT_TYPES; i++) {
            uint32 prompt_id = prompts[i];
            prompts_array[i] = prompt_id;
        }
        
        metaPrompt.burnForImageGeneration(prompts_array);

        // merge prompt ids and mint the card
        uint256 mergedPrompts = _mergePrompts(prompts);
        uint256 cardId = metaCard.mint(msg.sender, mergedPrompts);
        // emit event
        emit CreateImage(msg.sender, cardId);
    }

    /**
     * Function called by the oracle to publish the IPFS CID.
     * @param IPFSCid IPFS CID associated to the image
     * @param imageId id of the image
     * @param to address of the user that minted the image
     */
    function imageMinted(uint256 IPFSCid, uint256 imageId, address to) public onlyOwner {
        emit ImageCreated(IPFSCid, imageId, to);
    }

    /**
     * Destroy an image. The sender has to send enough ethers.
     * This function is called by the user when he wants to destroy an image.
     * Prompts are recovered and minted to the user.
     * @param imageId the id of the image to destroy
     */
    function burnImageAndRecoverPrompts(uint256 imageId) public payable checkCost(DESTRUCTION_FEES) isOwnerOf(imageId, metaCard){
        // burn the image
        metaCard.destroyCard(imageId);

        // recover the prompts
        uint256 imageIdShifted = imageId >> 64; //remove seed
        for(uint8 i = 0; i < NUM_PROMPT_TYPES; i++){
            uint32 currentPromptId = uint32(imageIdShifted & 0xffffffff);
            if (currentPromptId != 0){ // avoid minting non existing prompts IDs
                // mint the prompt
                metaPrompt.mint(msg.sender, currentPromptId);
            }
            imageIdShifted = imageIdShifted >> 32;
        }

        // emit event
        emit DestroyImage(imageId, msg.sender);
    }

    function _buyToken(uint256 tokenId, Sellable meta) private isTokenListed(tokenId, meta) returns (address, uint256){
        uint256 token_cost = meta.getTokenCost(tokenId);
        require(msg.value >= token_cost + TRANSACTION_FEES, "You didn't send enough ethers!");
        address seller = meta.ownerOf(tokenId);
        _payAddress(seller, token_cost);
        meta.transferFrom(seller, msg.sender, tokenId);
        return (seller, token_cost);
    }

    /**
     * This function can be called by users to buy a packet.
     * @param packetId the id of the packet to buy
     */
    function buyPacket(uint32 packetId) public payable {
        (address seller, uint256 packet_cost) = _buyToken(packetId, metaPacket);
        emit PacketTransfered(msg.sender, seller, packetId, packet_cost);
    }

    /**
     * This function can be called by users to buy a prompt.
     * @param promptId the id of the prompt to buy
     */
    function buyPrompt(uint32 promptId) public payable {
        (address seller, uint256 prompt_cost) = _buyToken(promptId, metaPrompt);
        emit PromptTransfered(msg.sender, seller, promptId, prompt_cost);
    }

    /**
     * This function can be called by users to express their will to buy a card.
     * They have to send an amount of ethers. An oracle will check if the amount is enough
     * and, if so, it will call the 'transferCard' function.
     * @param cardId the id of the card to buy
     */
    function buyCard(uint256 cardId) public payable {
        // this function registers the will of the buyer to buy a listed card
        (address seller, uint256 card_cost) = _buyToken(cardId, metaCard);
        emit CardTransfered(msg.sender, seller, cardId, card_cost);
    }

    /**
     * This function allows the contract to send ether to an address.
     * This is used to send ethers to the seller when a packet is sold.
     * @param _to the address to send the ether to
     * @param value the amount of ether to send
     */
    function _payAddress(address _to, uint256 value) private {
        (bool sent,) = _to.call{value: value}("");
        require(sent, "Failed to send Ether");
    }

    /**
     * List a packet. Listing means that the owner of the packet allows the contract to transfer it.
     * @param packetId the id of the packet to list
     * @param price the price of the packet
     */
    function listPacket(uint32 packetId, uint256 price) public {
        metaPacket.listToken(packetId, price);
        emit UpdateListPacket(packetId, price, true, msg.sender);
    }

    /**
     * List a prompt. Listing means that the owner of the prompt allows the contract to transfer it.
     * @param promptId the id of the prompt to list
     * @param price the price of the prompt
     */
    function listPrompt(uint32 promptId, uint256 price) public {
        metaPrompt.listToken(promptId, price);
        emit UpdateListPrompt(promptId, price, true, msg.sender);
    }

    /**
     * List an image. Listing means that the owner of the image allows the contract to transfer it.
     * @param cardId the id of the image to list
     * @param price the price of the image
     */
    function listCard(uint256 cardId, uint256 price) public {
        metaCard.listToken(cardId, price);
        emit UpdateListImage(cardId, price, true, msg.sender);
    }

    /**
     * Unlist a packet. Unlisting means that the owner of the packet doesn't allow the contract to transfer it anymore.
     * 
     * It sets the approval to address(0).
     * @param packetId the id of the packet to unlist
     */
    function unlistPacket(uint32 packetId) public {
        metaPacket.unlistToken(packetId);
        emit UpdateListPacket(packetId, 0,  false, msg.sender);
    }

    /**
     * Unlist a prompt. Unlisting means that the owner of the prompt doesn't allow the contract to transfer it anymore.
     * 
     * It sets the approval to address(0).
     * @param promptId the id of the prompt to unlist
     */
    function unlistPrompt(uint32 promptId) public {
        metaPrompt.unlistToken(promptId);
        emit UpdateListPrompt(promptId, 0, false, msg.sender);
    }

    /**
     * Unlist an image. Unlisting means that the owner of the image doesn't allow the contract to transfer it anymore.
     * 
     * It sets the approval to address(0).
     * @param cardId the id of the image to unlist
     */
    function unlistCard(uint256 cardId) public {
        metaCard.unlistToken(cardId);
        emit UpdateListImage(cardId, 0, false, msg.sender);
    }

    receive() external payable {} // to support receiving ETH by default
    fallback() external payable {}
    

    function terminate() public onlyOwner {
        selfdestruct(payable(owner));
    }
}