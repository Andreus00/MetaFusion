// SPDX-License-Identifier: MIT

/**
    This contract implements the cards for the MetaFusion system.
    This is based on the ERC721 standard, but with some modifications.

    A card can only be minted by the oracle, so the mint function must check
    that the caller is the oracle.
    The oracle is the only one who can mint new cards.

    The owner of the contract is the only one who can terminate the contract.
    The owner of a card can decide to burn it and get back the prompts used
    to mint it. This implies tha the card must track the prompts used to mint it.
    This is done by storing the prompts in a mapping indexed by the card id.
    
    The card also has a "seed" which is used to generate the prompts. This
    seed is stored in a mapping indexed by the card id.
    
    Everytime a card is transferred, the prompts must be transferred as well.
*/

pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./Prompt.sol";
/*
struct ImageMetadata {
    uint256 seed;
    uint[5] prompts;
    bool is_finalized;
}
*/

/**
 * CARD ENCODING
 * 256 bits uint
 * [ MSB
 *  NUM_PROMPT_TYPES x 32 bits,
 *  64 bits of random seed
 * ]LSB
 */

contract MetaCard is ERC721 {

    address private minter;  // the oracle
    address private owner;  // the owner of the contract; alias president
    
    string public baseURI = "https://metafusion.io/api/card/";  // The base URI for the metadata of the cards

	modifier onlyMinter() {
        require(msg.sender == minter, "You're not the minter!");
        _;
    }

    constructor() ERC721("MetaCard", "MCD") { // The name and symbol of the token
        minter = msg.sender;    // I still don't know how to use the oracle
        owner = msg.sender;    // The owner of the contract is the one who deployed it
    }

    function breakImage() payable public returns(uint32[] memory){
        // TODO 
        return new uint32[](0);
    }

    function mint(address to, uint256 cardPrompts) public onlyMinter returns(uint256) {
        // The oracle is the only one who can mint new cards.
        // calculate the 64 bits of the seed
        uint256 seed = uint256(keccak256(abi.encodePacked(cardPrompts, block.timestamp)));
        cardPrompts = (cardPrompts << 64) | (seed >> (256 - 64)); // put the seed into the first 64 bits 

        _safeMint(to, cardPrompts);
        // metadata[id].seed = _seed;
        // metadata[id].prompts = _prompts;
        // metadata[id].is_finalized = false;
        return cardPrompts;
    }

    function transfer(address to, uint id) public {
        require(msg.sender == ownerOf(id), "Only the owner of the card can transfer it!");
        _transfer(msg.sender, to, id);
    }
}