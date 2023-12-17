import {
    time,
    loadFixture,
  } from "@nomicfoundation/hardhat-toolbox/network-helpers";
  import { anyValue } from "@nomicfoundation/hardhat-chai-matchers/withArgs";
  import { expect } from "chai";
  import { ethers } from "hardhat";
  import { describe } from "mocha";


describe("HelloToken", function () {
    // We define a fixture to reuse the same setup in every test.
    // We use loadFixture to run this setup once, snapshot that state,
    // and reset Hardhat Network to that snapshot in every test.
    async function deployHelloToken() {  
      // Contracts are deployed using the first signer/account by default
      const [owner, otherAccount] = await ethers.getSigners();
  
      const HelloToken = await ethers.getContractFactory("HelloToken");
      const helloToken = await HelloToken.deploy();
  
      return { helloToken, owner, otherAccount };
    }
  
    describe("Deployment", function () {
      it("Check on the deployment", async function () {
        const { owner, otherAccount } = await loadFixture(deployHelloToken);
        
        // check the existance of the accounts
        expect(owner.address === undefined).to.be.false;
        expect(otherAccount.address === undefined).to.be.false;
        expect(owner.address).to.not.equal(otherAccount.address);

      });
    });
  
    describe("Minting", function () {
        it("Check minting for owner", async function () {
            const { helloToken, owner, otherAccount } = await loadFixture(deployHelloToken);
            // get the price of the token
            const price = await helloToken.PRICE();
            // set the sender to owner
            await helloToken.connect(owner);
            // mint 1000 tokens to owner
            await helloToken.mint({ value: ethers.parseEther("1000") });
            // check the balance of owner
            expect(await helloToken.checkBalance()).to.equal(ethers.parseEther("1000") / price);
        });
    });
  
    describe("Transfers", function () {
        it("Check transfer", async function () {
            const { helloToken, owner, otherAccount } = await loadFixture(
            deployHelloToken
            );
            // get the price of the token
            const price = await helloToken.PRICE();
            // set the sender to owner
            await helloToken.connect(owner);
            // mint 1000 tokens to owner
            await helloToken.mint({ value: ethers.parseEther("1000") });
            // check the balance of owner
            expect(await helloToken.checkBalance()).to.equal(ethers.parseEther("1000") / price);
            // check the balance of otherAccount
            expect(await helloToken.connect(otherAccount).checkBalance()).to.equal(ethers.parseEther("0"));
            // transfer 100 tokens from owner to otherAccount
            await helloToken.transfer(ethers.parseEther("100"), otherAccount.address);
            // check the balance of owner
            expect(await helloToken.checkBalance()).to.equal(ethers.parseEther("1000") / price - ethers.parseEther("100"));
            // check the balance of otherAccount
            expect(await helloToken.connect(otherAccount).checkBalance()).to.equal(ethers.parseEther("100"));
        });
    });
  });
  