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

contract MetaPrompt is ERC721 {

    address private minter;  // the oracle
    address private owner;  // the owner of the contract

    uint private constant GENERATION_COST = 0.1 ether;  // The cost of generating an image

    uint private constant NUM_PROMPT_TYPES = 5;  // The number of different prompt types

    mapping (uint => bool) private frozen;  // true if the prompt is frozen, false otherwise

    mapping (uint => uint[2]) public collection_type;  // The collection and type to which the prompt belongs. Everyone can read this.

    string public baseURI = "https://metafusion.io/api/prompt/";  // The base URI for the metadata of the prompts

    constructor() ERC721("MetaPrompt", "PRM") { // The name and symbol of the token
        minter = msg.sender;    // I still don't know how to use the oracle
        owner = msg.sender;    // The owner of the contract is the one who deployed it
    }

    function setOracle(address _oracle) public {
        // The owner of the contract is the only one who can set the oracle.
        require(msg.sender == owner, "Only the owner of the contract can set the oracle!");
        minter = _oracle;
    }

    /**
     * 
     * @param to The address of the receiver
     * @param id The hash of the prompt (keccak256(prompt + "series number"))
     * @param _collection The collection to which the prompt belongs
     * @param _type The type of the prompt
     */
    function mint(address to, uint id, uint _collection, uint _type) public {
        // The oracle is the only one who can mint new prompts.
        require(msg.sender == minter, "Only the oracle can mint new prompts!");
        _safeMint(to, id);
        collection_type[id][0] = _collection;
        collection_type[id][1] = _type;
    }

    function freeze(uint id) private {
        require(msg.sender == ownerOf(id), "Only the owner of the prompt can freeze it!");
        require(!frozen[id], "The prompt is already frozen!");
        frozen[id] = true;
    }

    function unfreeze(uint id) private {
        require(msg.sender == ownerOf(id), "Only the owner of the prompt can unfreeze it!");
        require(frozen[id], "The prompt is already unfrozen!");
        frozen[id] = false;
    }

    function isFrozen(uint id) public view returns (bool) {
        return frozen[id];
    }

    function createImage(uint[5] memory _prompts) public payable{
        /**
         * This function first checks if all the requirements are met, then freezes
         * the prompts and finally calls the oracle to mint the image.
         */
        // first check if the ether sent is enough
        require(msg.value >= GENERATION_COST, "Not enough ether sent!");
        // then check that the sender owns all the prompts
        for (uint i = 0; i < NUM_PROMPT_TYPES; i++) {
            // if the prompt is 0, then it is not used
            if (_prompts[i] != 0) {
                require(msg.sender == ownerOf(_prompts[i]), "Only the owner of the prompts can create an image!");
                require(!frozen[_prompts[i]], "The prompt is frozen!");
                require(collection_type[_prompts[i]][0] == collection_type[_prompts[0]][0], "The prompts must belong to the same collection!");
                require(collection_type[_prompts[i]][1] == i, "The prompts must be of the correct type!");
            }
        }
        // then freeze all the prompts
        for (uint i = 0; i < NUM_PROMPT_TYPES; i++) {
            freeze(_prompts[i]);
        }
        // TODO: now send all the prompts to the oracle to mint the image
        // TODO: mock the oracle for now
    }
}