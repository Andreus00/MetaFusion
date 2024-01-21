# Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a script that deploys that contract.

Try running some of the following tasks:

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat run scripts/deploy.ts
```

## Webapi server
The webapi server expose some rest api using Fast API package
install dependencies with following commands:
```shell
pip install fastapi
pip install "uvicorn[standard]"
```