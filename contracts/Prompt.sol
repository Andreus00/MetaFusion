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

    address private minter;  // the oracle
    address private owner;  // the owner of the contract

    uint32 public immutable NUM_PROMPT_TYPES;  // The number of different prompt types
    
    mapping (address => uint32[]) private prompt_list;  // TODO: remove this as it is only for debugging. 
                                                        // The list of prompts owned by an address. Everyone can read this.

    string public baseURI = "https://metafusion.io/api/prompt/";  // The base URI for the metadata of the prompts

    modifier onlyOwner() {
        require(msg.sender == owner, "You're not the owner!");
        _;
    }

	modifier onlyMinter() {
        require(msg.sender == minter, "You're not the minter!");
        _;
    }

    constructor(uint32 _NUM_PROMPT_TYPES) ERC721("MetaPrompt", "PRM") { // The name and symbol of the token
        minter = msg.sender;    // I still don't know how to use the oracle
        owner = msg.sender;    // The owner of the contract is the one who deployed it
        NUM_PROMPT_TYPES = _NUM_PROMPT_TYPES;
    }

    function setOracle(address _oracle) public onlyOwner {
        // The owner of the contract is the only one who can set the oracle.
        minter = _oracle;
    }

    /**
     * 
     * @param to The address of the receiver
     * @param id The hash of the prompt (keccak256(prompt + "series number"))
     */
    function mint(address to, uint32 id) public onlyMinter {
        // The oracle is the only one who can mint new prompts.
        _safeMint(to, uint256(id));
        prompt_list[to].push(id);
    }

    function getPromptsOwnebBy(address _address) public view returns (uint32[] memory) {
        return prompt_list[_address];
    }

    function getCollectionId(uint32 promptId) public pure returns (uint16){
        return uint16(promptId & 0x1fff);
    }

    function getPromptType(uint32 promptId) public pure returns (uint8){
        return uint8((promptId >> 13) & 0x7);
    }

    function removeElementFromArray(uint256 index, address caller) private{
        prompt_list[caller][index] = prompt_list[caller][prompt_list[caller].length - 1];
        prompt_list[caller].pop();
    }

    function removePromts(uint32[] memory prompts, address caller) public onlyOwner{
        uint8 elementsToRemove = 0;
        // count elements != 0
        for(uint8 ii = 0; ii < prompts.length; ii++){
            if(prompts[ii] != 0){
                elementsToRemove += 1;
            }
        }
        uint256 i = 0;
        while (elementsToRemove >= 1){
            bool isInList = false;
            // check if prompt is in list
            for(uint8 promptIndex = 0; promptIndex < prompts.length; promptIndex ++){
                isInList = prompt_list[caller][i] == prompts[promptIndex];
                if(isInList){
                    break;
                }
            }
            if(isInList){
                removeElementFromArray(i, caller);
                elementsToRemove --;
                continue;  // do not update i
            }
            i++;
        }
        // this is a fast workaround, since it suffer from 
    }

    function burnForImageGeneration(address promptOwner, uint32[] memory _prompts) public onlyOwner {
        /**
         * This function first checks if all the requirements are met, then freezes
         * the prompts and finally calls the oracle to mint the image.
         */
        // first check if the ether sent is enough
        // then check that the sender owns all the prompts
        
        uint8 invalidPrompts = 0;
        for (uint8 i = 0; i < NUM_PROMPT_TYPES; i++) {
            // if the prompt is 0, then it is not used
            uint16 collectionId = getCollectionId(_prompts[0]);
            if (_prompts[i] != 0) {
                require(promptOwner == ownerOf(_prompts[i]), "Only the owner of the prompts can create an image!");
                require(getCollectionId(_prompts[i]) == collectionId, "The prompts must belong to the same collection!");
                require(getPromptType(_prompts[i]) == i, "The prompts must be of the correct type!");

                // burn the prompt
                _burn(_prompts[i]);
            }
            else {
                invalidPrompts++;
            }
        }
        if (invalidPrompts == NUM_PROMPT_TYPES) {
            revert("No prompts used!");
        }
    }
}