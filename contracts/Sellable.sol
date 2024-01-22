// SPDX-License-Identifier: MIT

/**
 * This contract implements the Sellable tokens for the MetaFusion system.
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
contract Sellable is ERC721 {


    /////////// CONSTANTS ///////////
    /**
     * The owner of the contract.
     */
    address immutable private owner;

    /////////// VARIABLES ///////////

    /**
     * The cost of a token.
     */
    mapping(uint256 => uint256) private tokenCost;

    /////////// MODIFIERS ///////////

    /**
     * Only owner modifier.
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "You're not the owner!");
        _;
    }

    /////////// CONSTRUCTOR ///////////

    /**
     * Constructor.
     */
    constructor(string memory name_, string memory symbol_) ERC721(name_, symbol_) { // The name and symbol of the token
        owner = msg.sender;    // The owner of the contract is the one who deployed it
    }

    /////////// FUNCTIONS ///////////

    /**
     * Get the cost of a token.
     */
    function getTokenCost(uint256 tokenId) public view returns(uint256) {
        return tokenCost[tokenId];
    }

    /**
     * Set the cost of a token.
     */
    function _setTokenCost(uint256 tokenId, uint256 cost) internal {
        tokenCost[tokenId] = cost;
    }


    /**
     * List a token.
     */
    function listToken(uint256 tokenId, uint256 cost) public onlyOwner {
        // set a cost
        _setTokenCost(tokenId, cost);
        // approve the MetaFusion contract to transfer the token
        super._approve(owner, tokenId, tx.origin);
    }

    /**
     * Unlist a token.
     */
    function unlistToken(uint256 tokenId) public onlyOwner {
        // set the cost to 0
        _setTokenCost(tokenId, 0);
        // remove the approval
        super._approve(address(0), tokenId, tx.origin);
    }

    /**
     * Check if a token is listed.
     */
    function isTokenListed(uint256 tokenId) public view returns(bool) {
        return tokenCost[tokenId] > 0 && super.getApproved(tokenId) == owner;
    }

    /**
     * Burn a token.
     */
    function burn(uint256 tokenId) internal {
        super._burn(tokenId);
        tokenCost[tokenId] = 0;
    }
}
