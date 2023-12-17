pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./Prompt.sol";
import "./Packet.sol";
import "./Card.sol";


contract MetaFusionPresident {

    address private minter;  // the oracle
    address immutable private owner;  // the owner of the contract

    MetaPrompt private metaPrompt;
    MetaPacket private metaPacket;
    MetaCard   private metaCard;

    mapping (address => ImageMetadata[]) public metadata;  // The seed used to generate the image. Everyone can read this.

    string public baseURI = "https://metafusion.io/api/";  // The base URI for the metadata of the cards

    constructor() { // The name and symbol of the token
        minter = msg.sender;    // I still don't know how to use the oracle
        owner = msg.sender;    // The owner of the contract is the one who deployed it
        metaPacket = new MetaPacket();
        metaPrompt = new MetaPrompt();
        metaCard = new MetaCard();
    }

    function buyPacket(uint collection) public payable{
        // metaPacket.
        metaPacket.mint(msg.sender, collection);
    }
    
    function mintCard(uint[5] memory _prompts) public payable {
        // The oracle is the only one who can mint new cards.
        // uint id = metaCard.mint(msg.sender, _prompts);
        // metadata[msg.sender].push(ImageMetadata(id, _prompts, false));
        
    }

    function _mintCard(uint[5] memory _prompts) private {
        // The oracle is the only one who can mint new cards.
        require(msg.sender == minter, "Only the oracle can mint new cards!");
        // metadata[msg.sender].push(ImageMetadata(id, _prompts, false));
        
    }

}