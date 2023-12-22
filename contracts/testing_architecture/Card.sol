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

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./Prompt.sol";

struct ImageMetadata {
    uint seed;
    uint[5] prompts;
    bool is_finalized;
}

contract MetaCard is ERC721 {

    address private oracle;  // the oracle
    address private owner;  // the owner of the contract; alias president

    mapping (uint => ImageMetadata) public metadata;  // The seed used to generate the image. Everyone can read this.

    string public baseURI = "https://metafusion.io/api/card/";  // The base URI for the metadata of the cards

    constructor() ERC721("MetaCard", "MCD") { // The name and symbol of the token
        oracle = msg.sender;    // I still don't know how to use the oracle
        owner = msg.sender;    // The owner of the contract is the one who deployed it
    }

    /**
     * 
     * @param to 
     * @param id 
     * @param _seed 
     * @param _prompts 
     */
    function mint(address to, uint id, uint _seed, uint[5] memory _prompts) public {
        // The oracle is the only one who can mint new cards.
        require(msg.sender == oracle, "Only the oracle can mint new cards!");
        _safeMint(to, id);
        metadata[id].seed = _seed;
        metadata[id].prompts = _prompts;
        metadata[id].is_finalized = false;
    }

    function transfer(address to, uint id) public {
        require(msg.sender == ownerOf(id), "Only the owner of the card can transfer it!");
        _transfer(msg.sender, to, id);
    }
}