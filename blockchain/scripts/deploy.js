const hre = require("hardhat");

async function main() {
  const Zakat = await hre.ethers.getContractFactory("Zakat");
  const zakat = await Zakat.deploy();
  await zakat.deployed();
  console.log("Zakat contract deployed to:", zakat.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
