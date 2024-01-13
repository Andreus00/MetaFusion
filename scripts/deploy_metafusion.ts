import { ethers } from "hardhat";

async function main() {
  
  const token = await ethers.deployContract("MetaFusionPresident");

  await token.waitForDeployment();

  console.log(
    'MetaFusionPresident deployed.');
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
