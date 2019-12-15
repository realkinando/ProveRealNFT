# ProveReal NFT

This directory is a truffle project with the following sub-directories:

 - Build (compiled contracts)
 - migrations (instructions for deployment)
 - test (unit tests)

It is recommended you test this using a unix based machine. To test the contract do the following terminal commands in the folder:

 1. npm install
 2. npm install -g ganache-cli
 3. ganache-cli
 4. (in a new tab) truffle test

The IssuanceTool subdirectory contains the code for the issuance tool - which is python based. To run this, go to the IssuanceTool Directory and run

  1. pip install Web3
  2. pip install requests
  3. python3 IssuanceTool.py

An Ethereum wallet file called Keystore.json has been provided. Its password is "TestPass01234TestPass". This wallet has been loaded with some test Ether for you to test the code.

To access the admin features of the contract do the following.
 1. Recover the following seed in Metamask - “Tornado sight oval process
    dutch talk hazard predict sport pudding venture river”
 2. Navigate to MyEtherWallet and log in using Metamask (while linked to Rinkeby)
 3. Use the contract ABI (IssuanceTool/PVAA2ABI.json) and the contract address '0x9Df67E0e4989FdBcB4Efd0026f9FE5cAcB58D527' to link to the contract
