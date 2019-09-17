var ProveRealCore = artifacts.require("./ProveRealCore.sol");
const BigNumber = require('bignumber.js');
const assert = require("chai").assert;
const truffleAssert = require("truffle-assertions");

contract("ProveRealCore", function(accounts){
  let proveRealCoreInstance;

  beforeEach(async() => {
    proveRealCoreInstance = await ProveRealCore.new();
  });

  afterEach(async() => {
    await proveRealCoreInstance.kill();
  });

  it("setIssuanceFee correctly sets fees when requested by contract owner", async()=>{
    let t1 = await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    console.log({'setIssuanceFee gas used' : t1.receipt.gasUsed});
    let issuanceFee = await proveRealCoreInstance.issuanceFee();
    assert.equal(issuanceFee.toString(),web3.utils.toWei("1","ether").toString(),"issuanceFee updated correctly");
  });

  it("setIssuanceFee prevents non contract owner from changing issuance fee", async()=>{
    await truffleAssert.reverts(proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")),{from:accounts[1]}));
  });

  // Tests if brand name registry can correctly set a brand, when requested by contract owner
  it("setBrand works correctly when called by contract owner", async()=>{
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    console.log({'setBrand gas used' : t1.receipt.gasUsed});
    let brandName = await proveRealCoreInstance.addressToBrand(accounts[1]);
    assert.equal(brandName,"Test01234","address points to brand");
    let address = await proveRealCoreInstance.brandToAddress("Test01234")
    assert.equal(accounts[1],address,"brand points to correct address")
  });

  it("setBrand prevents non contract owner from setting up a brand", async()=>{
    await truffleAssert.reverts(proveRealCoreInstance.setBrand(accounts[1],"Test01234",{from:accounts[1]}));
  });

  it("setBrand prevents contract owner from overwritting a registered brand", async()=>{
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await truffleAssert.reverts(proveRealCoreInstance.setBrand(accounts[2],"Test01234"));
  });

  it("setBrand prevents non contract owners from overwritting a registered brand", async()=>{
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await truffleAssert.reverts(proveRealCoreInstance.setBrand(accounts[2],"Test01234",{from:accounts[2]}));
  })

  it("setBrand prevents the registration of a brand to an address already owning a brand", async()=>{
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await truffleAssert.reverts(proveRealCoreInstance.setBrand(accounts[1],"Test56789"));
  })

  // Tests if brand name registry correctly processes a request to assign a brand address, that is sent by the the contract owner
  it("changeBrandAddress works correctly when called by contract owner", async()=>{
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    let t3 = await proveRealCoreInstance.changeBrandAddress(accounts[1],accounts[2]);
    console.log({'changeBrandAddress gas used' : t3.receipt.gasUsed});
    let brandName2 = await proveRealCoreInstance.addressToBrand(accounts[2]);
    assert.equal(brandName2,"Test01234","changeBrandAddress works correctly");
    let brandName3 = await proveRealCoreInstance.addressToBrand(accounts[1]);
    assert.equal(brandName3,"","Former brand addresses do not point to the brand name");
  });

  it("changeBrandAddress works correctly when called by brand owner", async()=>{
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    let t3 = await proveRealCoreInstance.changeBrandAddress(accounts[1],accounts[2],{from:accounts[1]});
    let brandName2 = await proveRealCoreInstance.addressToBrand(accounts[2]);
    assert.equal(brandName2,"Test01234","changeBrandAddress works correctly");
    let brandName3 = await proveRealCoreInstance.addressToBrand(accounts[1]);
    assert.equal(brandName3,"","Former brand addresses do not point to the brand name");
  });

  it("changeBrandAddress prevents non contract owner parties to change brand addresses for brands they do not own",async()=>{
        let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
        await truffleAssert.reverts(proveRealCoreInstance.changeBrandAddress(accounts[1],accounts[2],{from:accounts[2]}));
    });

  it("changeBrandAddress prevents the changing of a brand address to an address already owning another brand", async()=>{
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    let t2 = await proveRealCoreInstance.setBrand(accounts[2],"Test56789");
    await truffleAssert.reverts(proveRealCoreInstance.changeBrandAddress(accounts[1],accounts[2]));
  });

  it("registerMetadata adds one new entry correctly", async()=>{
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    let t2 = await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    console.log({'registerMetadata gas used ' : t2.receipt.gasUsed});
    let metadata = await proveRealCoreInstance.getBrandItemByIndex(0,"Test01234");
    assert(metadata,"metadataURI000","Metadata correctly obtained from index in brand metadata mapping");
    let metadataID = await proveRealCoreInstance.getMetadataIndex("metadataURI000");
    assert(metadataID,0,"Correct metadataID returned");
  });

  it("registerMetadata prevents brands from double entering metadata they already registered", async()=> {
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    let t2 = await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await truffleAssert.reverts(proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]}),"");
  });

  // brand cannot register metadata registered by another brand
  it("registerMetadata prevents brands from registering metadata registered by another brand", async()=> {
    let t1 = await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    let t2 = await proveRealCoreInstance.setBrand(accounts[2],"Test56789");
    let t3 = await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await truffleAssert.reverts(proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[2]}));
  });

  // metadata ids are incremented correctly for multiple brands
  it("getBrandMetadataCount returns the expected value", async()=> {
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await proveRealCoreInstance.registerMetadata("metadataURI001",{from:accounts[1]});
    await proveRealCoreInstance.registerMetadata("metadataURI002",{from:accounts[1]});
    let metadataCount = await proveRealCoreInstance.getBrandMetadataCount("Test01234");
    assert.equal(metadataCount,3,"correct value returned")
  });

  it("isMetadataRegistered returns correct", async()=> {
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await proveRealCoreInstance.registerMetadata("metadataURI001",{from:accounts[1]});
    await proveRealCoreInstance.registerMetadata("metadataURI002",{from:accounts[1]});
    let md0 = await proveRealCoreInstance.isMetadataRegistered("metadataURI000");
    let md1 = await proveRealCoreInstance.isMetadataRegistered("metadataURI001");
    let md2 = await proveRealCoreInstance.isMetadataRegistered("metadataURI002");
    assert(md0,"");
    assert(md1,"");
    assert(md2,"");
  });

  it("getBrandItemByIndex works correctly", async()=> {
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.setBrand(accounts[2],"Test56789");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await proveRealCoreInstance.registerMetadata("metadataURI001",{from:accounts[1]});
    await proveRealCoreInstance.registerMetadata("metadataURI002",{from:accounts[1]});
    await proveRealCoreInstance.registerMetadata("metadataURI010",{from:accounts[2]});
    await proveRealCoreInstance.registerMetadata("metadataURI011",{from:accounts[2]});
    await proveRealCoreInstance.registerMetadata("metadataURI012",{from:accounts[2]});
    let md0 = await proveRealCoreInstance.getBrandItemByIndex(0,"Test01234");
    let md1 = await proveRealCoreInstance.getBrandItemByIndex(1,"Test01234");
    let md2 = await proveRealCoreInstance.getBrandItemByIndex(2,"Test01234");
    let md10 = await proveRealCoreInstance.getBrandItemByIndex(0,"Test56789");
    let md11 = await proveRealCoreInstance.getBrandItemByIndex(1,"Test56789");
    let md12 = await proveRealCoreInstance.getBrandItemByIndex(2,"Test56789");
    assert.equal("metadataURI000",md0,"");
    assert.equal("metadataURI001",md1,"");
    assert.equal("metadataURI002",md2,"");
    assert.equal("metadataURI010",md10,"");
    assert.equal("metadataURI011",md11,"");
    assert.equal("metadataURI012",md12,"");
  })

  it("Test issuance with correct fee, address and registered metadata", async()=>{
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    let t3 = await proveRealCoreInstance.issue(accounts[2],"metadataURI000",{value:new BigNumber(web3.utils.toWei("1","ether")),from:accounts[1]});
    console.log({'issue gas used' : t3.receipt.gasUsed});
    let issuer = await proveRealCoreInstance.tokenBrands(0);
    assert.equal("Test01234",issuer,"Brand set for certificate correctly");
    let metadata = await proveRealCoreInstance.tokenURI(0);
    assert.equal("metadataURI000",metadata,"Metadata set for certificate correctly");
    let itemOwner = await proveRealCoreInstance.ownerOf(0);
    assert(accounts[2],itemOwner,"certificate given to correct Ethereum address")
  });

  it("Issuance fails when incorrect fee is used", async() => {
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await truffleAssert.reverts(proveRealCoreInstance.issue(accounts[0],"metadataURI000"),"",{from:accounts[1]});
  });

  it("Issuance fails when non-brand address is used", async() => {
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await truffleAssert.reverts(proveRealCoreInstance.issue(accounts[3],"metadataURI000",{from:accounts[2],value:web3.utils.toWei("1","ether")}),"");
  });

  it("Issuance fails when metadata is not registered", async() => {
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await truffleAssert.reverts(proveRealCoreInstance.issue(accounts[2],"metadataURI000",{from:accounts[1],value:web3.utils.toWei("1","ether")}),"");
  });

  it("Issuance fails when brand uses metadata they do not own", async() => {
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.setBrand(accounts[2],"Test56789");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await truffleAssert.reverts(proveRealCoreInstance.issue(accounts[3],"metadataURI000",{from:accounts[2],value:web3.utils.toWei("1","ether")}),"");
  });

  it("Brand enumeration is added to correctly after issuance", async() => {
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.setBrand(accounts[3],"Test56789");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await proveRealCoreInstance.registerMetadata("metadataURI001",{from:accounts[3]});
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    await proveRealCoreInstance.issue(accounts[2],"metadataURI000",{value:new BigNumber(web3.utils.toWei("1","ether")),from:accounts[1]});
    await proveRealCoreInstance.issue(accounts[2],"metadataURI001",{value:new BigNumber(web3.utils.toWei("1","ether")),from:accounts[3]});
    await proveRealCoreInstance.issue(accounts[2],"metadataURI000",{value:new BigNumber(web3.utils.toWei("1","ether")),from:accounts[1]});
    let noTokens = await proveRealCoreInstance.getNumberOfBrandTokens("Test01234");
    assert.equal(noTokens,2,"tokens added to brand enumeration");
    let tokenId = await proveRealCoreInstance.getTokenIDFromBrandEnumeration(1,"Test01234");
    assert.equal(tokenId,2,"getTokenIDFromBrandEnumeration works correctly");
    let tokenIndex = await proveRealCoreInstance.issuedTokensIndex(tokenId);
    assert.equal(1,tokenIndex,"issuedTokensIndex contains correct data")

  });

  it("burn correctly removes token from brand enumeration", async() => {
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    await proveRealCoreInstance.issue(accounts[2],"metadataURI000",{value:new BigNumber(web3.utils.toWei("1","ether")),from:accounts[1]});
    await proveRealCoreInstance.issue(accounts[2],"metadataURI000",{value:new BigNumber(web3.utils.toWei("1","ether")),from:accounts[1]});
    console.log("issued");
    let noTokens = await proveRealCoreInstance.getNumberOfBrandTokens("Test01234");
    console.log({"noTokens":noTokens.toString()});
    let owner = await proveRealCoreInstance.ownerOf(0);
    console.log({"owner" : owner});
    console.log({"acc 2" : accounts[2]})
    await proveRealCoreInstance.burn(0,{from:accounts[2]});
    console.log("burned");
    noTokens = await proveRealCoreInstance.getNumberOfBrandTokens("Test01234");
    assert.equal(noTokens,1,"token deleted from brand enumeration");
  });

  it("withdrawBalance allows owner to withdraw balance", async() => {
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    await proveRealCoreInstance.issue(accounts[2],"metadataURI000",{value:new BigNumber(web3.utils.toWei("1","ether")),from:accounts[1]});
    let initial = await web3.eth.getBalance(accounts[0]);
    let withdraw = await proveRealCoreInstance.withdrawBalance();
    let after = await web3.eth.getBalance(accounts[0]);
    let cost = new BigNumber(20000000000*withdraw.receipt.gasUsed);
    initial = new BigNumber(initial);
    after = new BigNumber(after);
    console.log({"withdrawBalance gas used" : withdraw.receipt.gasUsed});
    assert(after.isEqualTo(initial.plus(new BigNumber(web3.utils.toWei("1","ether"))).minus(cost)),
    "owner balance after withdrawl is equal to initially + 1eth - cost of calling withdraw");
  });

  it("withdrawBalance prevents non-owners from withdrawing balance", async() => {
    await proveRealCoreInstance.setBrand(accounts[1],"Test01234");
    await proveRealCoreInstance.registerMetadata("metadataURI000",{from:accounts[1]});
    await proveRealCoreInstance.setIssuanceFee(new BigNumber(web3.utils.toWei("1","ether")));
    await proveRealCoreInstance.issue(accounts[2],"metadataURI000",{value:new BigNumber(web3.utils.toWei("1","ether")),from:accounts[1]});
    await truffleAssert.reverts(proveRealCoreInstance.withdrawBalance({from:accounts[3]}));
  });


});
