// SPDX-License-Identifier: MIT

import {
    time,
    loadFixture,
  } from "@nomicfoundation/hardhat-toolbox/network-helpers";
  import { anyValue } from "@nomicfoundation/hardhat-chai-matchers/withArgs";
  import { expect } from "chai";
  import { ethers } from "hardhat";
  import { describe } from "mocha";


describe("MetafusionPresident", function () {

    // async function switchAccount(metaFusionPresident, otherAccount) {
    //   return await metaFusionPresident.connect(otherAccount);
    //
    // }
    
    // We define a fixture to reuse the same setup in every test.
    // We use loadFixture to run this setup once, snapshot that state,
    // and reset Hardhat Network to that snapshot in every test.
    async function deployMetafusionPresident() {
      // Contracts are deployed using the first signer/account by default
      const [owner, otherAccount] = await ethers.getSigners();
      const MetaFusionPresident = await ethers.getContractFactory("MetaFusionPresident");
      const metaFusionPresident = await MetaFusionPresident.deploy();
      
      return { metaFusionPresident, owner, otherAccount };
    }

    async function deployMetafusionAndLogWithOther() {
      // Contracts are deployed using the first signer/account by default
      const [owner, otherAccount] = await ethers.getSigners();
  
      const MetaFusionPresident = await ethers.getContractFactory("MetaFusionPresident");
      const mfp = await MetaFusionPresident.deploy();

      const metaFusionPresident = await mfp.connect(otherAccount);
      
      return { metaFusionPresident, owner, otherAccount };
    }

    async function deployMetafusionAndCreateCollection() {
      // Contracts are deployed using the first signer/account by default
      const [owner, otherAccount] = await ethers.getSigners();
  
      const MetaFusionPresident = await ethers.getContractFactory("MetaFusionPresident");
      const metaFusionPresident = await MetaFusionPresident.deploy();

      // Forge a collection
      await metaFusionPresident.forgeCollection(0);        // Forge a collection
      
      return { metaFusionPresident, owner, otherAccount };
    }
  
    describe("ForgeCollection", function () {
      it("Forge a collection", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionPresident);

        // check if the collection is not forged
        expect(await metaFusionPresident.checkCollectionExistence(0)).to.equal(false);

        // Forge a collection
        await metaFusionPresident.forgeCollection(0);

        // check if the collection is forged
        expect(await metaFusionPresident.checkCollectionExistence(0)).to.equal(true);
        expect(await metaFusionPresident.checkCollectionExistence(1)).to.equal(false);
      });

      it("Refuse to forge a collection", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionAndLogWithOther);
        
        expect(await metaFusionPresident.checkCollectionExistence(0)).to.equal(false);

        // Forge a collection
        await expect(metaFusionPresident.forgeCollection(0)).to.be.revertedWith("Only the owner of the contract can forge new collections!");

        // check if the collection is NOT forged
        expect(await metaFusionPresident.checkCollectionExistence(0)).to.equal(false);
        expect(await metaFusionPresident.checkCollectionExistence(1)).to.equal(false);
      });
    });
    describe("forgePacket", function () {
      it("Not enought money sent.", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionPresident);

        await expect(metaFusionPresident.forgePacket(0)).to.be.revertedWith("You didn't send enought ethers!");
      });

      it("Buy a packet whose collection does NOT exist.", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionPresident);

        await expect(metaFusionPresident.forgePacket(0, { value: ethers.parseEther("0.1")})).to.be.revertedWith("The collection does not exist!");
      });


      it("Buy a packet whose collection does exist.", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionAndCreateCollection);

        // check if the collection is forged
        expect(await metaFusionPresident.checkCollectionExistence(0)).to.equal(true);
        
        // get the balance of the wallet
        let user_balance: bigint = await ethers.provider.getBalance(otherAccount.address);

        // the user buy a packet from the collection
        expect(await metaFusionPresident.forgePacket(0, { value: ethers.parseEther("0.1")})).to.not.be.reverted;

        // check the nwe balance of the wallet
        let new_balance: bigint = await ethers.provider.getBalance(otherAccount.address);

        // check if the balance has decreased
        expect((user_balance - new_balance) == ethers.parseEther("0.1"));
      });
    });
  });
  