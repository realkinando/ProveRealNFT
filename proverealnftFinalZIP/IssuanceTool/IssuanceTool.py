from PinataGateway import PinataGateway
from PVAAGateway import PVAAGateway
import os
import json
from getpass import getpass
from web3.auto import w3

class IssuanceTool():

    def __init__(self):
        self.__pvaaGateway = None
        self.__pinataGateway = None
        self.__apiWalletFileName = None

    def updateNonce(self):
        pass

    def menu(self):
        print("\n\t Welcome Back ",self.__pvaaGateway.getBrand())
        while True:
            try:
                option = int(input("\n\n\t Select Option : \n\t (0) Issue Certificate \t (1) Track Issued Certificates \n\t (2) Create New Metadata \t (3) View Current Metadata \n\t (4) View Ethereum Address & Balance \t (5) Send Ether \n\t (6) Exit Program\n"))
                if option == 0:
                    self.issue()
                elif option == 1:
                    self.viewBrandTokens()
                elif option == 2:
                    self.registerMetadata()
                elif option == 3:
                    self.viewMetadata()
                elif option == 4:
                    self.getAddress()
                    self.getBalance()
                elif option == 5:
                    self.sendEth()
                elif option == 6:
                    break
                else:
                    print("Option was invalid")
            except:
                print("Option was invalid")
                continue
        quit()




    def issue(self):
        while True:
            try:
                print("Fee is currently : ", w3.fromWei(self.__pvaaGateway.getFee(),"ether"),"Eth")
                addressTo = input("Paste Ethereum Address of Receipient")
                self.viewMetadata()
                metadataURI = self.__pvaaGateway.getMetadataObjectList()[int(input("Select Index of Metadata to use"))]["uri"]
                print(metadataURI)
                self.__pvaaGateway.issue(addressTo,metadataURI)
                break
            except Exception as e:
                #raise
                print(e)
                tryAgain = input("Something went wrong, try again (Y/N)")
                if tryAgain.lower() != 'y':
                    break

    def viewBrandTokens(self):
        printTable(["id","owner","uri"],self.__pvaaGateway.getBrandTokens())

    def registerMetadata(self):
        while True:
            try:
                print('\tList of Images')
                print('\tINDEX\t FILE')
                fileList = getFilesOfType(os.getcwd(),'jpg')
                listFiles(fileList)
                print("\t------------------------------------")
                imageFile = fileList[int(input("Select Index of Image File to Use"))]
                name = input("Enter item name")
                description = input("Enter item description")
                imageUploadDict = self.__pinataGateway.fileUpload(imageFile)
                image_url = "https://gateway.pinata.cloud/ipfs/" + imageUploadDict["IpfsHash"]
                metadata = {"name":name,"description":description,"image_url":image_url}
                metadataUploadDict = self.__pinataGateway.jsonUpload(metadata)
                metadataURI = "https://gateway.pinata.cloud/ipfs/" +metadataUploadDict["IpfsHash"]
                self.__pvaaGateway.registerMetadata(metadataURI)
                break
            except Exception as e:
                #raise
                print(e)
                tryAgain = input("Something went wrong, try again (Y/N)")
                if tryAgain.lower() != 'y':
                    break


    def viewMetadata(self):
        self.__pvaaGateway.updateMetadataObjectList()
        printTable(["INDEX","name","description","image_url"],self.__pvaaGateway.getMetadataObjectList())

    def getAddress(self):
        print("\tEthereum Address : ",self.__pvaaGateway.getAddress())

    def getBalance(self):
        print("\tBalance : ",w3.fromWei(self.__pvaaGateway.getBalance(),"ether")," Eth")

    def sendEth(self):
        while True:
            try:
                addressTo = input("Paste Ethereum Address of Receipient")
                wei = w3.toWei(input("Enter amount in Eth to send"),'ether')
                self.__pvaaGateway.sendEth(wei,addressTo)
                break
            except Exception as e:
                #raise
                print(e)
                tryAgain = input("Something went wrong, try again (Y/N)")
                if tryAgain.lower() != 'y':
                    break

    def login(self):
        while True:
            try:
                print("""
                                  @@*
    %@@@@#                       &@@        @@@@@#                  @@@@
    %@  .@, %%%.%#    %%#   ,,  .@@   %%*   @@  *@,   %%*    *%#(%    %@
    %@@@@@  ,@@  @@ @@* #@% #@  @@. &@* @@  @@@@@&  @@  @@  @@  @@    %@
    %@       @@     @@   @&  @@@@&  @@,,.,  @@  %@  @@,,.,  @@  @@    %@
    %@      @@@@&    @@@@*   #@@@    &@@@*  @@  %@   &@@@*   @@@*@@ @@@@@@
                """)
                print("\n\tWelcome to the ProveReal Brand Issuance Tool, Please Login In\n")
                print("\t------------------------------------")
                print('\tList of LoadFiles')
                print('\tINDEX\t FILE')
                fileList = getFilesOfType(os.getcwd(),'json')
                listFiles(fileList)
                print("\t------------------------------------")
                keyfile = fileList[int(input('\tSelect index of Ethereum Wallet Keyfile'))]
                self.__apiWalletFileName = fileList[int(input('\tSelect index of API Key \ Wallet Data file'))]
                with open(self.__apiWalletFileName) as awf:
                    apiWalletFile = json.load(awf)
                password = getpass(prompt="\tEnter Password")
                print("\t------------------------------------\n")
                apiKey = apiWalletFile['apiKey']
                secretAPIKey = apiWalletFile['secretAPIKey']
                projectID = apiWalletFile['projectID']
                nonceCount = apiWalletFile['nonceCount']
                print('\tLoading Ethereum Wallet...')
                self.__pvaaGateway = PVAAGateway(keyfile,password,projectID,nonceCount)
                print('\tLoading IPFS Gateway...')
                self.__pinataGateway = PinataGateway(apiKey,secretAPIKey)
                print("\n\t------------------------------------\n\t------------------------------------")
                self.menu()
                break
            except Exception as e:
                #raise
                print(e)
                tryAgain = input("Something went wrong, try again (Y/N)")
                if tryAgain.lower() != 'y':
                    quit()

def printTable(keys,dictList):
    print("")
    longestAtts = []
    for i in keys:
        longestAtts.append(len(i)+5)
    for i in dictList:
        for j in range(len(keys)):
            if keys[j] == "INDEX":
                pass
            elif len(str(i[keys[j]])) > longestAtts[j]:
                longestAtts[j] = len(str(i[keys[j]]))+5
    for i in range(-1,len(dictList)):
        printStr='\t'
        for j in range(len(keys)):
            if i == -1:
                printStr += keys[j].ljust(longestAtts[j])
            else :
                if keys[j] == "INDEX":
                    printStr += str(i).ljust(longestAtts[j])
                else:
                    printStr += str(dictList[i][keys[j]]).ljust(longestAtts[j])
        print(printStr)
        if i == -1:
            printStr = "\t"
            for i in longestAtts:
                printStr += ("-"*i)
            print(printStr)


def getFilesOfType(path,fileType):
    all = os.listdir(path)
    ofType = []
    for i in all:
        if fileType in i:
            ofType.append(i)
    #print(ofType)
    return ofType

def listFiles(fileList):
    for i in range(len(fileList)):
        print('\t',i,'\t',fileList[i])


if __name__ == "__main__":
    IssuanceTool().login()
