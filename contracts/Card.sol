// SPDX-License-Identifier: MIT

/**
    This contract implements the cards for the MetaFusion system.
    This is based on the ERC721 standard, but with some modifications.
    
    Functions can only be called by the owner of the contract. In metafusion the owner is the MetaFusionPresident.
*/

pragma solidity ^0.8.19;

import "./Sellable.sol";

/**
 * CARD ENCODING
 * 256 bits uint
 * [ MSB
 *  NUM_PROMPT_TYPES x 32 bits,
 *  64 bits of pseudo random seed
 * ]LSB
 */

contract MetaCard is Sellable {


    /////////// CONSTRUCTOR ///////////

    /**
     * Constructor.
     */
    constructor() Sellable("MetaCard", "MCD") {} // The name and symbol of the token


    /////////// FUNCTIONS ///////////

    /**
     * Burn a card.
     */
    function destroyCard(uint256 imageId) public onlyOwner{
        super.burn(imageId);
    }

    /**
     * Mint a new card.
     * 
     * Minting consists of generating a pseudo random seed and storing it in the first 64 bits of the card.
     * Then the image is minted with _safeMint (ERC721).
     * 
     * The id of the card is finally returned.
     */
    function mint(address to, uint256 cardPrompts) public onlyOwner returns(uint256) {
        // The oracle is the only one who can mint new cards.
        // calculate the 64 bits of the seed
        uint256 seed = uint256(keccak256(abi.encodePacked(cardPrompts, block.timestamp)));
        cardPrompts = (cardPrompts << 64) | (seed >> (256 - 64)); // put the seed into the first 64 bits 

        _safeMint(to, cardPrompts);
        
        return cardPrompts;
    }
}