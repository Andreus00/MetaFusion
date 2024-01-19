// SPDX-License-Identifier: MIT

/**
 * This contract implements the Prompt for the MetaFusion system.
 * This is based on the ERC721 standard, but with some modifications.
 * 
 * A Prompt can only be minted by the oracle.
 * 
 * The owner of the contract is the only one who can terminate the contract.
 * 
 * The owner of some Prompts can decide to merge them and create an Image.
 * The image is created by the oracle, so the merge function first freezes the prompts
 * and then calls the oracle to mint the image.
 * 
 * The Prompt has a "collection" which is the collection to which the prompt
 * belongs. This is stored in a mapping indexed by the prompt id.
 */

pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
/**
 * ID: 0-12 collection
 *    13-15 prompt type
 *    16-28 packet id in collection
 *    29-31 sequence number of the prompt in packet
 * 	  [31, 30, 29, 28, 27, 26, 25, 24, 23, 22, ... , 3, 2, 1, 0]
 *  */
contract MetaPrompt is ERC721 {

    address private owner;  // the owner of the contract

    uint32 public immutable NUM_PROMPT_TYPES;  // The number of different prompt types

    modifier onlyOwner() {
        require(msg.sender == owner, "You're not the owner!");
        _;
    }

    constructor(uint32 _NUM_PROMPT_TYPES) ERC721("MetaPrompt", "PRM") { // The name and symbol of the token
        owner = msg.sender;    // The owner of the contract is the one who deployed it
        NUM_PROMPT_TYPES = _NUM_PROMPT_TYPES;
    }

    /**
     * 
     * @param to The address of the receiver
     * @param id The hash of the prompt (keccak256(prompt + "series number"))
     */
    function mint(address to, uint32 id) public onlyOwner {
        // The oracle is the only one who can mint new prompts.
        _safeMint(to, uint256(id));
    }

    function _getCollectionId(uint32 promptId) private pure returns (uint16){
        return uint16(promptId & 0x1fff);
    }

    function _getPromptType(uint32 promptId) private pure returns (uint8){
        return uint8((promptId >> 13) & 0x7);
    }

    function burnForImageGeneration(address promptOwner, uint32[] memory _prompts) public onlyOwner {
        /**
         * This function first checks if all the requirements are met, then freezes
         * the prompts and finally calls the oracle to mint the image.
         */
        // first check if the ether sent is enough
        // then check that the sender owns all the prompts
        require(_prompts[0] != 0, "Character prompt is missing!");
        uint8 invalidPrompts = 0;
        for (uint8 i = 0; i < NUM_PROMPT_TYPES; i++) {
            // if the prompt is 0, then it is not used
            uint16 collectionId = _getCollectionId(_prompts[0]);
            if (_prompts[i] != 0) {
                require(promptOwner == ownerOf(_prompts[i]), "Only the owner of the prompts can create an image!");
                require(_getCollectionId(_prompts[i]) == collectionId, "The prompts must belong to the same collection!");
                require(_getPromptType(_prompts[i]) == i, "The prompts must be of the correct type!");
            }
            else {
                invalidPrompts++;
            }
        }
        if (invalidPrompts == NUM_PROMPT_TYPES) {
            revert("No prompts used!");
        }
        for (uint8 i = 0; i < NUM_PROMPT_TYPES; i++) {
            if (_prompts[i] != 0){
                _burn(_prompts[i]);
            }
    	}	
    }

	function approve(address to, uint256 tokenId) public override onlyOwner {
        _approve(to, tokenId, tx.origin);
    }
}
