pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/Strings.sol";

contract HelloToken {

    address public minter;

    mapping (address => uint) public balance;

    uint public constant PRICE = 2;
    // uint public constant PRICE = 2 finney;
    // finney is no longer a supported denomination since Solidity v.0.7.0

    constructor() {
        minter = msg.sender;
    }

    function mint() public payable {
        require(msg.value >= PRICE, string(abi.encodePacked("Not enough value for a token! ", Strings.toString(msg.value), " < ", Strings.toString(PRICE))));
        balance [msg.sender] += msg.value / PRICE;
        // Guess guess, where does the remainder of the msg.value end?
    }
    function transfer(uint amount, address to) public {
        require(balance[msg.sender] >= amount, "Not enough tokens!");
        balance[msg.sender] -= amount;
        balance[to] += amount;
    }
    function checkBalance() public view returns (uint) {
        return balance[msg.sender];
    }
    function terminate() public {
        require(msg.sender == minter, "You cannot terminate the contract!");
        selfdestruct(payable(minter));
    }
}