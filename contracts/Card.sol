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

contract MetaCard is ERC721 {

    address private minter;  // the oracle
    address private owner;  // the owner of the contract

    mapping (uint => uint) public seed;  // The seed used to generate the image. Everyone can read this.
    mapping (uint => uint[5]) public prompts;  // The prompts used to mint the card. Everyone can read this.

    string public baseURI = "https://metafusion.io/api/card/";  // The base URI for the metadata of the cards

    constructor() ERC721("MetaCard", "MCD") { // The name and symbol of the token
        minter = msg.sender;    // I still don't know how to use the oracle
        owner = msg.sender;    // The owner of the contract is the one who deployed it
    }

    function mint(address to, uint id, uint _seed, uint[5] memory _prompts) public {
        // The oracle is the only one who can mint new cards.
        require(msg.sender == minter, "Only the oracle can mint new cards!");
        _safeMint(to, id);
        seed[id] = _seed;
        prompts[id] = _prompts;

        // TODO: add the prompt freezing logic. This first needs the Prompt contract to be implemented.
    }

    function burn(uint id) public {
        require(msg.sender == ownerOf(id), "Only the owner of the card can burn it!");
        // TODO: add the prompt unfreezing logic. This first needs the Prompt contract to be implemented.

        // Burn the card
        _burn(id);

    }

    function transfer(address to, uint id) public {
        require(msg.sender == ownerOf(id), "Only the owner of the card can transfer it!");
        _transfer(msg.sender, to, id);
    }
}