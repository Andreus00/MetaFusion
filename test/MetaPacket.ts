// SPDX-License-Identifier: MIT

import {
    time,
    loadFixture,
  } from "@nomicfoundation/hardhat-toolbox/network-helpers";
  import { anyValue } from "@nomicfoundation/hardhat-chai-matchers/withArgs";
  import { expect } from "chai";
  import { ethers } from "hardhat";
  import { describe } from "mocha";
import { metafusionPresidentSol } from "../typechain-types/factories/contracts/testing_architecture";


describe("MetafusionPresident", function () {

    function genPKUUID(collection: number | bigint | boolean, idInCollection: number | bigint | boolean){
      return (BigInt(idInCollection) << BigInt(16)) | BigInt(collection)
    }

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
      const {metaFusionPresident, owner, otherAccount} = await deployMetafusionPresident();

      // Forge a collection
      await metaFusionPresident.forgeCollection(0);        // Forge a collection
      
      return { metaFusionPresident, owner, otherAccount };
    }

    async function deployMetafusionCreateCollectionThenSwitchAccount() {
      const {metaFusionPresident, owner, otherAccount } = await deployMetafusionAndCreateCollection()
      const mfp = await metaFusionPresident.connect(otherAccount);
      return { mfp, owner, otherAccount };
    }

    async function deployMetafusionAndOpenPacket() {
      let { metaFusionPresident, owner, otherAccount } = await deployMetafusionAndCreateCollection();
      
      // Forge a packet
      let etherAmount = { value: ethers.parseEther("1.0")}
      await metaFusionPresident.forgePacket(0, etherAmount)

      let collection = BigInt(0);
      let idInCollection = BigInt(1);
      let pkUUID = genPKUUID(collection, idInCollection);

      // Open the packet
      await metaFusionPresident.openPacket(pkUUID)
            
      return { metaFusionPresident, owner, otherAccount };
    }

    async function deployMetafusionAndOpenPacketThenSwitchAccount() {
      const {metaFusionPresident, owner, otherAccount } = await deployMetafusionAndOpenPacket()
      const mfp = await metaFusionPresident.connect(otherAccount);
      return { mfp, owner, otherAccount };
    }

    async function deployMetafusionAndGenerateImage() {
      const {metaFusionPresident, owner, otherAccount } = await deployMetafusionAndOpenPacket()
      const NUM_PROMPTS = await metaFusionPresident.PACKET_SIZE();

      let promptList = await metaFusionPresident.getPromptsOwnebBy(owner.address);

      let prompts = [0, 0, 0, 0, 0, 0];
      for (let i = 0; i < NUM_PROMPTS; i++) {
        let promptId = promptList[i];
        let promptType = Number((promptId >> BigInt(13)) & BigInt(0x7));
        prompts[promptType] = Number(promptId);
      }

      const tx = await metaFusionPresident.createImage(prompts, { value: ethers.parseEther("0.1") });
      const receipt = await tx.wait();
      const log = receipt?.logs[receipt?.logs.length - 1];
      let data = log?.topics[1];
      const imageId = data;
      return { metaFusionPresident, owner, otherAccount, imageId };
    }

    async function OpenTwoPacketsWithDiffAccount() {
      // init the contract, forge a collection and a packet, open the packet
      const {metaFusionPresident, owner, otherAccount } = await deployMetafusionAndOpenPacket()

      // switch account
      const metaFusionPresidentOther = await metaFusionPresident.connect(otherAccount);

      // forge a collection and a packet
      let etherAmount = { value: ethers.parseEther("1.0")}
      await metaFusionPresidentOther.forgePacket(0, etherAmount)

      let collection = BigInt(0);
      let idInCollection = BigInt(2);
      let pkUUID = genPKUUID(collection, idInCollection);

      // Open the packet
      await metaFusionPresidentOther.openPacket(pkUUID)
      return { metaFusionPresident, metaFusionPresidentOther, owner, otherAccount };
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

    describe("OpenPacket", function () {
      let etherAmount = { value: ethers.parseEther("1.0")}
      
      it("Open a correct packet", async function () {
        const { mfp, owner, otherAccount } = await loadFixture(deployMetafusionCreateCollectionThenSwitchAccount);
        let collectionForged = BigInt(0);
        let idInCollection = BigInt(1);

        await expect(mfp.forgePacket(0, etherAmount))
                .to.emit(mfp, "PacketForged").withArgs(otherAccount.address, genPKUUID(collectionForged, idInCollection)); //uint32(idInCollection) << 16 | uint32(_collection)
        await expect(mfp.openPacket(genPKUUID(collectionForged, idInCollection)))
          .to.emit(mfp, "PacketOpened");
      })

     
      it("Open a packet owned by another user", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionAndCreateCollection);
        let collectionForged = BigInt(0);
        let idInCollection = BigInt(1);
        
        // make a new packet
        await expect(metaFusionPresident.forgePacket(0, etherAmount))
                .to.emit(metaFusionPresident, "PacketForged").withArgs(owner.address, genPKUUID(collectionForged, idInCollection)); //uint32(idInCollection) << 16 | uint32(_collection)
        
        // connect to another account
        const mfp = await metaFusionPresident.connect(otherAccount);

        // try to steal the packet
        await expect(mfp.openPacket(genPKUUID(collectionForged, idInCollection)))
                      .to.be.revertedWith("Only the owner of the packet can burn it!")

     })

     it("Open a packet that not exist", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionAndCreateCollection);
        let collectionForged = BigInt(0);
        let idInCollection = BigInt(1);
        
        // make a new packet
        await expect(metaFusionPresident.forgePacket(collectionForged, etherAmount))
                .to.emit(metaFusionPresident, "PacketForged");
        

        // try to open non existing packet
        await expect(metaFusionPresident.openPacket(genPKUUID(collectionForged, idInCollection))).to.not.be.reverted;
      })

      it("Open a packet of not existing collection", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionAndCreateCollection);
        let collectionForged = BigInt(0);
        let idInCollection = BigInt(1);
        
        // make a new packet
        await expect(metaFusionPresident.forgePacket(collectionForged, etherAmount))
                .to.emit(metaFusionPresident, "PacketForged");
        

        // try to open packet of non existing collection
        let wrongCollection = BigInt(420);
        await expect(metaFusionPresident.openPacket(genPKUUID(wrongCollection, idInCollection))).to.be.reverted;

      })

      it("Open a packet twice", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionAndCreateCollection);
        let collectionForged = BigInt(0);
        let idInCollection = BigInt(1);
        
        // make a new packet
        await expect(metaFusionPresident.forgePacket(collectionForged, etherAmount))
                .to.emit(metaFusionPresident, "PacketForged");
        

        // try to open twise the packet
        await expect(metaFusionPresident.openPacket(genPKUUID(collectionForged, idInCollection))).to.not.be.reverted;
        await expect(metaFusionPresident.openPacket(genPKUUID(collectionForged, idInCollection))).to.be.reverted;
      })

      it("Check Prompts generation", async function () {
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionAndOpenPacket);
        const NUM_PROMPTS = await metaFusionPresident.PACKET_SIZE();
        
        // check if all the prompts have been added to the account
        let promptList = await metaFusionPresident.getPromptsOwnebBy(owner.address);
        // check that the list contains 6 unique prompts
        expect(promptList.length).to.equal(NUM_PROMPTS);
        expect(new Set(promptList).size).to.equal(NUM_PROMPTS);
      })

      it("Check ", function(){}
      )
    });
    describe("Image", function () {
      it("Create an image", async function(){
        const { metaFusionPresident, owner, otherAccount } = await loadFixture(deployMetafusionAndOpenPacket);
        const NUM_PROMPTS = await metaFusionPresident.PACKET_SIZE();

        let promptList = await metaFusionPresident.getPromptsOwnebBy(owner.address);


        let prompts = [0, 0, 0, 0, 0, 0];
        for (let i = 0; i < NUM_PROMPTS; i++) {
          let promptId = promptList[i];
          let promptType = Number((promptId >> BigInt(13)) & BigInt(0x7));
          prompts[promptType] = Number(promptId);
        }
        
        expect (await metaFusionPresident.createImage(prompts, { value: ethers.parseEther("0.1") })).to.emit(metaFusionPresident, "CreateImage");

        let cardsOwned = await metaFusionPresident.getCardsOwnedBy(owner.address);
        expect(cardsOwned.length).to.equal(1);
      })

      it("Refuse to create an image", async function(){
        const { mfp, owner, otherAccount } = await loadFixture(deployMetafusionAndOpenPacketThenSwitchAccount);
        const NUM_PROMPTS = await mfp.PACKET_SIZE();

        let promptList = await mfp.getPromptsOwnebBy(owner.address);


        let prompts = [0, 0, 0, 0, 0, 0];
        for (let i = 0; i < NUM_PROMPTS; i++) {
          let promptId = promptList[i];
          let promptType = Number((promptId >> BigInt(13)) & BigInt(0x7));
          prompts[promptType] = Number(promptId);
        }
        
        expect(mfp.createImage(prompts, { value: ethers.parseEther("0.1") })).to.be.revertedWith("Only the owner of the prompts can create an image!");
      })

      it("Generate two images", async function(){
        const { metaFusionPresident, metaFusionPresidentOther, owner, otherAccount } = await loadFixture(OpenTwoPacketsWithDiffAccount);
        const NUM_PROMPTS = await metaFusionPresident.PACKET_SIZE();

        let promptListOwner = await metaFusionPresident.getPromptsOwnebBy(owner.address);
        expect(promptListOwner.length).to.equal(NUM_PROMPTS);
        let promptListOther = await metaFusionPresident.getPromptsOwnebBy(otherAccount.address);
        expect(promptListOther.length).to.equal(NUM_PROMPTS);

        let packPrompts = function (promptList: bigint[]) {
          let prompts = [0, 0, 0, 0, 0, 0];
          for (let i = 0; i < NUM_PROMPTS; i++) {
            let promptId = promptList[i];
            let promptType = Number((promptId >> BigInt(13)) & BigInt(0x7));
            prompts[promptType] = Number(promptId);
          }
          return prompts;
        }
        let checkPrompts = async function (mfp: any, prompts: number[], address: string) {
          expect(await mfp.createImage(prompts, { value: ethers.parseEther("0.1") })).to.emit(metaFusionPresident, "CreateImage");
          let cardsOwned = await mfp.getCardsOwnedBy(address);
          expect(cardsOwned.length).to.equal(1);
        }

        let promptsOwner = packPrompts(promptListOwner);
        let promptsOther = packPrompts(promptListOther);

        await checkPrompts(metaFusionPresident, promptsOwner, owner.address);
        await checkPrompts(metaFusionPresidentOther, promptsOther, otherAccount.address);
      });

      it("Destroy an image", async function(){
        const { metaFusionPresident, owner, otherAccount, imageId } = await loadFixture(deployMetafusionAndGenerateImage);
        console.log("imageId", imageId);
        console.log("logged_account", await metaFusionPresident.getAddress());
        console.log("owner", owner.address);
        expect(await metaFusionPresident.burnImageAndRecoverPrompts(imageId)).to.not.be.reverted;
      });
    });
  });
  