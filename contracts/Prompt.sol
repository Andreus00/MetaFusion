// SPDX-License-Identifier: MIT

/**
 * This contract implements the Prompt for the MetaFusion system.
 * This is based on the ERC721 standard, but with some modifications.
 * 
 * Functions can only be called by the owner of the contract. In metafusion the owner is the MetaFusionPresident.
 */

pragma solidity ^0.8.19;

import "./Sellable.sol";
/**
 * ID: 0-12 collection
 *    13-15 prompt type
 *    16-28 packet id in collection
 *    29-31 sequence number of the prompt in packet
 * 	  [31, 30, 29, 28, 27, 26, 25, 24, 23, 22, ... , 3, 2, 1, 0]
 *  */
contract MetaPrompt is Sellable {


    /////////// CONSTANTS ///////////
    
    /**
     * The number of different prompt types.
     */
    uint32 public immutable NUM_PROMPT_TYPES;
    
    /////////// CONSTRUCTOR ///////////

    /**
     * Constructor.
     */
    constructor(uint32 _NUM_PROMPT_TYPES) Sellable("MetaPrompt", "PRM") { // The name and symbol of the token
        NUM_PROMPT_TYPES = _NUM_PROMPT_TYPES;
    }

    /////////// FUNCTIONS ///////////

    /**
     * Mint a new prompt.
     * @param to The address of the receiver
     * @param id The hash of the prompt (keccak256(prompt + "series number"))
     */
    function mint(address to, uint32 id) public onlyOwner {
        // The oracle is the only one who can mint new prompts.
        _safeMint(to, uint256(id));
    }

    /**
     * Get the collection id of a prompt.
     */
    function _getCollectionId(uint32 promptId) private pure returns (uint16){
        return uint16(promptId & 0x1fff);
    }

    /**
     * Get the prompt type of a prompt.
     */
    function _getPromptType(uint32 promptId) private pure returns (uint8){
        return uint8((promptId >> 13) & 0x7);
    }

    /**
     * Burn a prompts to generate an image.
     * 
     * This function is called by users through the MetaFusionPresident contract.
     * 
     * The type of prompts in the array are:
     * character    0
     * hat          1
     * handoff      2
     * color        3
     * eyes         4
     * style        5
     * 
     * The user can send 0 for the prompts that are not used.
     * The character prompt is mandatory.
     */
    function burnForImageGeneration(uint32[] memory _prompts) public onlyOwner {
        // first check if the ether sent is enough
        require(_prompts[0] != 0, "Character prompt is missing!");
        // then check that the sender owns all the prompts
        for (uint8 i = 0; i < NUM_PROMPT_TYPES; i++) {
            // if the prompt is 0, then it is not used
            if (_prompts[i] != 0) {
                uint16 collectionId = _getCollectionId(_prompts[0]);
                // check that the sender owns the prompt, that it is of the correct type and that it belongs to the same collection
                require(tx.origin == ownerOf(_prompts[i]), "Only the owner of the prompts can create an image!");
                require(_getCollectionId(_prompts[i]) == collectionId, "The prompts must belong to the same collection!");
                require(_getPromptType(_prompts[i]) == i, "The prompts must be of the correct type!");
            }
        }
        // burn the prompts
        for (uint8 i = 0; i < NUM_PROMPT_TYPES; i++) {
            if (_prompts[i] != 0){
                burn(_prompts[i]);
            }
    	}
    }
}
