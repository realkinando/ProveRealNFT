from web3 import Web3
from web3.auto import w3
from web3.middleware import geth_poa_middleware
import json, requests

PVAA2ADDRESS = '0x9Df67E0e4989FdBcB4Efd0026f9FE5cAcB58D527' #Contract address
ENDPOINTHALF = 'https://rinkeby.infura.io/v3/' #used to access Infura
CHAINID = 4
GASPRICE = w3.toWei('1', 'gwei') #default gas price on Rinkeby

class PVAAGateway:

    def __init__(self,kfile,password,projectID,nonceCount,local=False,address=PVAA2ADDRESS,endpoint=None):
        with open(kfile) as keyfile:
            #Reads keyfile
            encryptedKey = keyfile.read()
            #Attepts to use password to decrypt Keystore - will throw if password is wrong or keyfile is invalid
            self.__privateKey = w3.eth.account.decrypt(encryptedKey, password)
        if local:
            self.__endpoint = endpoint
        else:
            self.__endpoint =  ENDPOINTHALF + projectID
        self.__web3 = Web3(Web3.HTTPProvider(self.__endpoint))
        #Required as Rinkeby is not fully compatible with the Ethereum network
        self.__web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        #If the projectID is invalid, the code below will throw an exception
        self.__web3.eth.getBlock('latest')
        with open("PVAA2ABI.json","r") as f:
            PVAA2ABI = json.load(f)
        self.__nonceCount = nonceCount
        #Creates a contract object, this is used to help generate transactions
        self.__pvaa2 = w3.eth.contract(address=address,abi=PVAA2ABI)
        #Recovers the account name of the user
        self.__address = w3.eth.account.privateKeyToAccount(self.__privateKey).address
        #Recovers the brand name of the user
        self.__brand = self.reconstructStr(self.sendCallHandler(self.__pvaa2.functions.addressToBrand(self.__address),33000))
        self.__MetadataStoredCount = 0
        self.__MetadataObjectList = []
        #retreives metadata tied to the brand
        self.updateMetadataObjectList()
        self.__MetadataStoredCount = self.getMetadataCount()

    def getAddress(self):
        return self.__address

    def getBrand(self):
        return self.__brand

    def getEndpoint(self):
        return self.__endpoint

    # reconstructs a string object from Hex Bytes object produced by Web3.py
    def reconstructStr(self,hexBO):
        charList = []
        for i in hexBO:
            if i != 0:
                charList.append(chr(i))
        return ''.join(charList).strip()

    # reconstructs an int object from Hex Bytes object produced by Web3.py
    def reconstructUInt256(self,hexBO):
        return int.from_bytes(bytes(hexBO),byteorder='big')

    # reconstructs an ethereum addres as a string object from Hex Bytes object produced by Web3.py
    def reconstructAddress(self,hexBO):
        return '0x'+repr(hexBO)[36:-2]

    # helper function for sending calls(transactions which do not effect the state of the network)
    def sendCallHandler(self,contractFunction,gas):
        tx = contractFunction.buildTransaction({
            'chainId': CHAINID,
            'gas':gas,
            'gasPrice': GASPRICE,
            'nonce' : self.__nonceCount
        })
        return self.__web3.eth.call(tx)

    # helper function for sending transactions
    def sendTxHandler(self,contractFunction,gas,value=0):
            while True:
                try:
                    tx = contractFunction.buildTransaction({
                        'chainId': CHAINID,
                        'gas': gas,
                        'gasPrice': GASPRICE,
                        'nonce' : self.__nonceCount,
                        'value' : value
                    })
                    signedTx = w3.eth.account.signTransaction(tx,private_key = self.__privateKey)
                    return self.__web3.eth.sendRawTransaction(signedTx.rawTransaction)
                    self.__nonceCount+=1
                except ValueError as e:
                    if 'nonce too low' in str(e):
                        self.__nonceCount+=1
                except:
                    raise
                # exception raising not working correctly!!!

    def getFee(self):
        return self.reconstructUInt256(self.sendCallHandler(self.__pvaa2.functions.issuanceFee(),30000))

    # Takes metadata URI, registers metadata via the PVAA2 registerMetadata method
    def registerMetadata(self,metadataURI):
        self.sendTxHandler(self.__pvaa2.functions.registerMetadata(metadataURI),200000)


    def issue(self,addressTo,metadataURI):
        self.sendTxHandler(self.__pvaa2.functions.issue(addressTo,metadataURI),500000,value = self.getFee())

    def getMetadataCount(self):
        return self.reconstructUInt256(self.sendCallHandler(self.__pvaa2.functions.getBrandMetadataCount(self.__brand),33000))

    def getBrandItemByIndex(self,index):
        return self.reconstructStr(self.sendCallHandler(self.__pvaa2.functions.getBrandItemByIndex(index,self.__brand),33000))[1:]

    def tokenURI(self,index):
        return self.reconstructStr(self.sendCallHandler(self.__pvaa2.functions.tokenURI(index),33000))[1:]

    def getNumberOfBrandTokens(self):
        return self.reconstructUInt256(self.sendCallHandler(self.__pvaa2.functions.getNumberOfBrandTokens(self.__brand),33000))

    def getTokenIDFromBrandEnumeration(self,index):
        return self.reconstructUInt256(self.sendCallHandler(self.__pvaa2.functions.getTokenIDFromBrandEnumeration(index,self.__brand),33000))

    # Used to send Eth
    def sendEth(self,wei,address,gas=21000):
        while True:
            try:
                tx = {
                        'to' : address,
                        'chainId':CHAINID,
                        'gas':gas,
                        'gasPrice' : GASPRICE,
                        'nonce' : self.__nonceCount,
                        'value' : wei
                }
                signedTx = w3.eth.account.signTransaction(tx,private_key = self.__privateKey)
                self.__nonceCount+=1
                return self.__web3.eth.sendRawTransaction(signedTx.rawTransaction)
            except ValueError as e:
                self.__nonceCount+=1
            except:
                raise

    def getBalance(self):
        return self.__web3.eth.getBalance(self.__address)

    # Used to obtain a metadata object of a givenID
    def fetchMetadataObj(self,i):
        uri = self.getBrandItemByIndex(i)
        r = requests.get(uri)
        metadataObject = r.json()
        metadataObject['uri'] = uri
        return metadataObject

    # checks if the amount of metadata on the network is greater than what it has. Fetches what it doesn't hold
    def updateMetadataObjectList(self):
        metadataCount =  self.getMetadataCount()
        if self.__MetadataStoredCount < metadataCount:
            for i in range(self.__MetadataStoredCount,metadataCount):
                self.__MetadataObjectList.append(self.fetchMetadataObj(i))
        self.__MetadataStoredCount = metadataCount

    def getMetadataObjectList(self):
        return self.__MetadataObjectList

    def ownerOf(self,id):
        return self.reconstructAddress(self.sendCallHandler(self.__pvaa2.functions.ownerOf(id),33000))

    # Returns token data as JSON
    def getBrandToken(self,i):
        id = self.getTokenIDFromBrandEnumeration(i)
        owner = self.ownerOf(id)
        uri = self.tokenURI(id)
        return {'id':id, 'owner':owner, 'uri':uri}


    def getBrandTokens(self):
        brandTokens = []
        for i in range(self.getNumberOfBrandTokens()):
            brandTokens.append(self.getBrandToken(i))
        return brandTokens
