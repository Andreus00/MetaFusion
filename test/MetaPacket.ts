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
    const NUM_PROMPT_TYPES = 10; // Adjust the value based on your contract

    function mergePrompts(prompts: number[]): number {
        let merged = BigInt(0);
        for (let i = 0; i < NUM_PROMPT_TYPES; i++) {
            merged = (merged << BigInt(32)) | BigInt(prompts[i]);
        }
        return Number(merged);
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
      let imageId = (await metaFusionPresident.getCardsOwnedBy(owner.address))[0];
      const usedPrompts = prompts.filter(n => n!=0);

      return { metaFusionPresident, owner, otherAccount, imageId, usedPrompts, promptList };
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
        
        await expect (metaFusionPresident.createImage(prompts, { value: ethers.parseEther("0.1") })).to.emit(metaFusionPresident, "CreateImage");

        let cardsOwned = await metaFusionPresident.getCardsOwnedBy(owner.address);
        expect(cardsOwned.length).to.equal(1);

        // check that prompts are correctly removed
        let updatedPromptList = await metaFusionPresident.getPromptsOwnebBy(owner.address);
        let usedPrompts = 0;
        // count non zeroes values
        for (let i = 0; i < prompts.length; i++) {
          if (prompts[i] !== 0) {
            usedPrompts++;
          }
        }
        // check length consistency
        // console.log("used", prompts, "updated", updatedPromptList,"full list", promptList , "used prompts", usedPrompts);
        // check if the length of the updated prompt list is equal to the length of the old prompt list and the prompt list
        expect(updatedPromptList.length).to.be.equal(promptList.length - usedPrompts);
        // check values consistency
        for(let i = 0; i < prompts.length; i++){
          if(prompts[i] !== 0){
            // check that used prompt is not in user prompts list
            expect(updatedPromptList.includes(BigInt(prompts[i]))).to.be.false
          }
        }
        // check that every unused prompts are in the user's prompts lists
        // remove all prompts used for image minting
        let expectedPromptList = promptList.filter(n => !prompts.includes(Number(n)));
        // just sort things for make same arrays in same order
        // Ensure the arrays are mutable
        expectedPromptList = [...expectedPromptList];
        updatedPromptList = [...updatedPromptList];
        expectedPromptList.sort();
        updatedPromptList.sort();
        // compare element to element way...
        expect(expectedPromptList.length == updatedPromptList.length);
        for(let i = 0; i < expectedPromptList.length; i++){
          expect(expectedPromptList[i] == updatedPromptList[i]).to.be.true;
        }
      }
      )

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
        
        await expect(mfp.createImage(prompts, { value: ethers.parseEther("0.1") })).to.be.revertedWith("Only the owner of the prompts can create an image!");
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
          await expect(mfp.createImage(prompts, { value: ethers.parseEther("0.1") })).to.emit(metaFusionPresident, "CreateImage");
          let cardsOwned = await mfp.getCardsOwnedBy(address);
          expect(cardsOwned.length).to.equal(1);
        }

        let promptsOwner = packPrompts(promptListOwner);
        let promptsOther = packPrompts(promptListOther);

        await checkPrompts(metaFusionPresident, promptsOwner, owner.address);
        await checkPrompts(metaFusionPresidentOther, promptsOther, otherAccount.address);
      });

      it("Destroy an image", async function(){
        const { metaFusionPresident, owner, otherAccount, imageId, usedPrompts, promptList } = await loadFixture(deployMetafusionAndGenerateImage);
        
        console.log("imageId", imageId, typeof(imageId));
        console.log("logged_account", await metaFusionPresident.getAddress());
        console.log("owner", owner.address);
        
        
        // check that new pompt list do not correspond to the previous one
        // Use await to resolve the promise
        const actualPrompts = await metaFusionPresident.getPromptsOwnebBy(owner.address);

        // Use .members to check if the arrays have the same elements (order-independent)
        expect(actualPrompts).to.have.not.members(usedPrompts);

        let tx = await metaFusionPresident.burnImageAndRecoverPrompts(imageId, { value: ethers.parseEther("0.1") });
        const receipt = await tx.wait();
        
        // Use await to resolve the promise
        const cardsOwned = await metaFusionPresident.getCardsOwnedBy(owner.address);

        // Use .equal to check if the resolved value is 0
        expect(cardsOwned.length).to.be.equal(0);
                
        // check that new pompt list correspond to the previous one
        // Use await to resolve the promise
        const newActualPrompts = await metaFusionPresident.getPromptsOwnebBy(owner.address);

        // Use .members to check if the arrays have the same elements (order-independent)
        console.log("old prompts", promptList, "new prompts", newActualPrompts);
        expect(newActualPrompts.length).to.be.equal(8);  
        
        let _newActualPrompts = newActualPrompts.map(value => BigInt(value));
        let _promptList = promptList.map(value => BigInt(value));
        expect(_newActualPrompts).to.have.members(_promptList);  
             
      });
    });
  });
  