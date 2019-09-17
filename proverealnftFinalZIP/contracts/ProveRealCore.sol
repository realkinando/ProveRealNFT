pragma solidity ^0.5.0;

//The ProveRealCore Contract imports these from OpenZeppelin
//Truffle gathers these files and includes them in the byte code for the contract
import 'openzeppelin-solidity/contracts/token/ERC721/ERC721Full.sol';
import 'openzeppelin-solidity/contracts/ownership/Ownable.sol';
import 'openzeppelin-solidity/contracts/token/ERC721/ERC721Burnable.sol';

//Our contract inherits from the imported contracts from ProveRealCore
contract ProveRealCore is ERC721Full,ERC721Burnable,Ownable{

  //Public variables have built in getters, accessible via methodName()

  // Mapping corresponding a brand to a list of tokenIDs representing what it has issued
  mapping(string => uint256[]) private _issuedTokens;
  // Mapping linking token's ID to its index in the brand enumeration
  mapping(uint256 => uint256) public issuedTokensIndex;
  // Mapping returning true or false if an address is a registered brand
  mapping(address => bool) private _addressIsBrand;
  // Mapping linking a token to its brand name
  mapping(uint256 => string) public tokenBrands;
  // Mapping linking an address to the brand name it represents
  mapping(address => string) public addressToBrand;
  // Mapping linking a brand to the address managing it
  mapping(string => address) private _brandToAddress;
  // Mapping returning if a brand has been assigned
  mapping(string => bool) private _brandAssigned;
  // Mapping of brandnames to a secondary mapping, in which metadata strings are linked to bools
  mapping(string => mapping(string => bool)) private _brandHasMetadata;
  // Mapping returning if a metadataURI is registered
  mapping(string => bool) private _metadataRegistered;
  // Mapping linking a metadata to its brand
  mapping(string => string) private _brandOfMetadata;
  //mapping linking a brand to a mapping of ints to metadataURIs, essentially serving as alternative to an array
  mapping(string => mapping(uint256 => string)) private _brandMetadataMapping;
  //mapping returning number of registered metadata items a brand has
  mapping(string => uint256) private _brandMetadataCount;
  //mapping returns the index the _brandMetadataMapping of a given metadataURI
  mapping(string => uint256) private _metadataIndex;
  //represents the fee required to issue, in wei (10^-18 Ether)
  uint256 public issuanceFee;
  //this event is emitted when a new token is issued
  event issued(string brand, uint256 tokenId);

  // constructor gives the token the name "ProveRealAlphaAlphaV2" and the symbol "PVAA"
  constructor() ERC721Full("ProveRealAlphaAlphaV2", "PVAA") public {
    issuanceFee = 0;
 }

 //Destroys contract, only used for testing purposes
 function kill() onlyOwner external{
   selfdestruct(msg.sender);
 }

// manually written getter, as solidity doesn't support public getters for variable length keys
 function brandToAddress(string calldata brand) external view returns(address){
   return _brandToAddress[brand];
 }

 // Checks if brand exists and if the address already has a brand... If neither : it assigns the address the given brandName
 // only contract owner can call this
 function setBrand(address brandAddress, string calldata brandName) external onlyOwner{
   require(!_brandAssigned[brandName]);
   require(!_addressIsBrand[brandAddress]);
   addressToBrand[brandAddress] = brandName;
   _addressIsBrand[brandAddress] = true;
   _brandAssigned[brandName] = true;
   _brandToAddress[brandName] = brandAddress;
 }

 // Checks if the caller is either the contract owner or oldAddress. If so and newAddress isn't a brand owner. the swap occurs
 function changeBrandAddress(address oldAddress, address newAddress) external {
   require(_addressIsBrand[oldAddress]);
   require(!_addressIsBrand[newAddress]);
   require(oldAddress == msg.sender || isOwner());
   string memory brandName = addressToBrand[oldAddress];
   delete addressToBrand[oldAddress];
   delete _addressIsBrand[oldAddress];
   addressToBrand[newAddress] = brandName;
   _addressIsBrand[newAddress] = true;
   _brandToAddress[brandName] = newAddress;
 }

// manually written getter, as solidity doesn't support public getters for variable length keys
 function getMetadataBrand(string calldata metadataURI) external view returns(string memory){
   return _brandOfMetadata[metadataURI];
 }

 // manually written getter, as solidity doesn't support public getters for variable length keys
 function getMetadataIndex(string calldata metadataURI) external view returns(uint256){
   return _metadataIndex[metadataURI];
 }

 // checks if msg.sender is a brand metadata hasn't been registered, if not then registers metadata to the calling addresses brand
 function registerMetadata(string calldata metadataURI) external validBrand{
   require(!_metadataRegistered[metadataURI]);
   string memory brand = addressToBrand[msg.sender];
   uint256 index = _brandMetadataCount[brand];
   _brandHasMetadata[brand][metadataURI] = true;
   _brandOfMetadata[metadataURI] = brand;
   _metadataRegistered[metadataURI] = true;
   _brandMetadataMapping[brand][index] = metadataURI;
   _brandMetadataCount[brand] = index + 1;
 }

 // manually written getter, as solidity doesn't support public getters for variable length keys
 function getBrandMetadataCount(string calldata brand) external view returns(uint256){
   return _brandMetadataCount[brand];
 }

 // manually written getter, as solidity doesn't support public getters for multi dimensional mappings
 function getBrandItemByIndex(uint256 index,string calldata brand) external view returns(string memory){
   return _brandMetadataMapping[brand][index];
 }

 // manually written getter, as solidity doesn't support public getters for variable length keys
 function isMetadataRegistered(string calldata metadataURI) external view returns(bool){
   return _metadataRegistered[metadataURI];
 }

 // Used internally within issuance to link a new token to its brand
 function _setTokenBrand(uint256 tokenId, string memory brand) internal {
    require(_exists(tokenId));
    tokenBrands[tokenId] = brand;
  }

  // Used internally when burning to remove a token from a brand's enumeration
  function _removeTokenFromBrandEnumeration(string memory brand, uint256 tokenId) internal {
    uint256  lastTokenIndex = _issuedTokens[brand].length.sub(1);
    uint256  tokenIndex = issuedTokensIndex[tokenId];

    // When the token to delete is the last token, the swap operation is unnecessary
    if (tokenIndex != lastTokenIndex) {
       uint256 lastTokenId = _issuedTokens[brand][lastTokenIndex];
      _issuedTokens[brand][tokenIndex] = lastTokenId; // Move the last token to the slot of the to-delete token
      issuedTokensIndex[lastTokenId] = tokenIndex; // Update the moved token's index
    }
    // This also deletes the contents at the last position of the array
    _issuedTokens[brand].length--;
  }

  // Used internally when issueing to add a token to a brand's enumeration
  function _addTokenToBrandEnumeration(string memory brand, uint256 tokenId) private {
       issuedTokensIndex[tokenId] = _issuedTokens[brand].length;
       _issuedTokens[brand].push(tokenId);
   }

   // manually written getter, as solidity doesn't support public getters for variable length keys
   function getNumberOfBrandTokens(string calldata brand) external view returns(uint256){
     return _issuedTokens[brand].length;
   }

   //manually written getter, as solidity doesn't support public getters for variable length keys
   function getTokenIDFromBrandEnumeration(uint256 tokenIndex, string calldata brand) external view returns(uint256){
     return _issuedTokens[brand][tokenIndex];
   }

   //Modifies the inherited _burn method from ERC721 to remove a token from a brand's enumeration
   function _burn(address owner, uint256 tokenId) internal{
     require(ownerOf(tokenId) == owner);
     string memory brand = tokenBrands[tokenId];
     _removeTokenFromBrandEnumeration(brand, tokenId);
     super._burn(owner, tokenId);
   }

   function _burn(uint256 tokenId) internal {
      _burn(ownerOf(tokenId), tokenId);
   }

   //Mints a token to send to the address to with the metadataURI given
   //Determines the brand of the sender
   //If the sender owns the supplied metadata, issuance goes ahead via the inherited _mint and _setTokenURI methods
   function issue(address to, string calldata metadataURI) external payable validBrand issuanceFeeCorrect{
     string memory brand = addressToBrand[msg.sender];
     require(_brandHasMetadata[brand][metadataURI]);
     uint256 id = totalSupply();
     _mint(to, id);
     _setTokenURI(id,metadataURI);
     _setTokenBrand(id,brand);
     _addTokenToBrandEnumeration(brand,id);
     emit issued(brand, id);
   }

   //used to set fee for issuing
   function setIssuanceFee(uint256 fee) external onlyOwner{
     issuanceFee = fee;
   }

   // used to withdraw collected Ether
   function withdrawBalance() external onlyOwner{
     msg.sender.transfer(address(this).balance);
   }

   modifier issuanceFeeCorrect(){
     require(msg.value == issuanceFee);
     _;
   }

   modifier validBrand(){
     require(_addressIsBrand[msg.sender]);
     _;
   }

}
